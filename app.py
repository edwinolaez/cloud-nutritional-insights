from flask import Flask, jsonify, request, redirect, session, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
import pandas as pd
import requests
import os

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
CORS(app, supports_credentials=True)

CSV_PATH = os.path.join(os.path.dirname(__file__), "All_Diets.csv")
df = pd.read_csv(CSV_PATH)

numeric_cols = ["Protein(g)", "Carbs(g)", "Fat(g)"]
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

# ── Static frontend ──────────────────────────────────────────────────────────

@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")

@app.route("/frontend/<path:filename>")
def frontend_files(filename):
    return send_from_directory("frontend", filename)

# ── Data API ─────────────────────────────────────────────────────────────────

@app.route("/api/insights")
def get_insights():
    avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()
    return jsonify(avg_macros.to_dict("index"))

@app.route("/api/recipes")
def get_recipes():
    diet_type = request.args.get("diet_type", None)
    if diet_type:
        filtered = df[df["Diet_type"] == diet_type]
        return jsonify(filtered.to_dict("records"))
    return jsonify(df.to_dict("records"))

# ── Auth status ───────────────────────────────────────────────────────────────

@app.route("/api/auth/status")
def auth_status():
    user = session.get("user")
    if user:
        return jsonify({"logged_in": True, "user": user})
    return jsonify({"logged_in": False})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"logged_in": False})

# ── Google OAuth ──────────────────────────────────────────────────────────────

GOOGLE_AUTH_URL    = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL   = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO    = "https://www.googleapis.com/oauth2/v3/userinfo"

@app.route("/auth/google")
def google_login():
    client_id    = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = "http://127.0.0.1:5000/auth/google/callback"
    params = (
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
    )
    return redirect(GOOGLE_AUTH_URL + params)

@app.route("/auth/google/callback")
def google_callback():
    code         = request.args.get("code")
    client_id    = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = "http://127.0.0.1:5000/auth/google/callback"

    token_resp = requests.post(GOOGLE_TOKEN_URL, data={
        "code":          code,
        "client_id":     client_id,
        "client_secret": client_secret,
        "redirect_uri":  redirect_uri,
        "grant_type":    "authorization_code",
    })
    access_token = token_resp.json().get("access_token")

    user_resp = requests.get(
        GOOGLE_USERINFO,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_resp.json()

    session["user"] = {
        "provider": "Google",
        "name":     user_info.get("name"),
        "email":    user_info.get("email"),
        "picture":  user_info.get("picture"),
    }
    return redirect("/?logged_in=google")

# ── GitHub OAuth ──────────────────────────────────────────────────────────────

GITHUB_AUTH_URL  = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO  = "https://api.github.com/user"

@app.route("/auth/github")
def github_login():
    client_id    = os.getenv("GITHUB_CLIENT_ID")
    redirect_uri = "http://127.0.0.1:5000/auth/github/callback"
    params = (
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=read:user%20user:email"
    )
    return redirect(GITHUB_AUTH_URL + params)

@app.route("/auth/github/callback")
def github_callback():
    code          = request.args.get("code")
    client_id     = os.getenv("GITHUB_CLIENT_ID")
    client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    redirect_uri  = "http://127.0.0.1:5000/auth/github/callback"

    token_resp = requests.post(GITHUB_TOKEN_URL, data={
        "code":          code,
        "client_id":     client_id,
        "client_secret": client_secret,
        "redirect_uri":  redirect_uri,
    }, headers={"Accept": "application/json"})
    access_token = token_resp.json().get("access_token")

    user_resp = requests.get(
        GITHUB_USERINFO,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_resp.json()

    session["user"] = {
        "provider": "GitHub",
        "name":     user_info.get("name") or user_info.get("login"),
        "email":    user_info.get("email"),
        "picture":  user_info.get("avatar_url"),
    }
    return redirect("/?logged_in=github")

# ── Azure Cleanup ─────────────────────────────────────────────────────────────

@app.route("/api/azure/status")
def azure_status():
    try:
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        resource_group  = os.getenv("AZURE_RESOURCE_GROUP")
        vm_name         = os.getenv("AZURE_VM_NAME")

        credential      = AzureCliCredential()
        compute_client  = ComputeManagementClient(credential, subscription_id)

        vm = compute_client.virtual_machines.get(resource_group, vm_name, expand="instanceView")
        statuses = vm.instance_view.statuses
        power_state = next(
            (s.display_status for s in statuses if s.code.startswith("PowerState")),
            "Unknown"
        )
        return jsonify({"vm": vm_name, "status": power_state})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/azure/deallocate", methods=["POST"])
def azure_deallocate():
    try:
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        resource_group  = os.getenv("AZURE_RESOURCE_GROUP")
        vm_name         = os.getenv("AZURE_VM_NAME")

        credential     = AzureCliCredential()
        compute_client = ComputeManagementClient(credential, subscription_id)

        # Deallocate stops the VM and releases compute resources (stops billing)
        compute_client.virtual_machines.begin_deallocate(resource_group, vm_name)
        return jsonify({"message": f"VM '{vm_name}' is being deallocated.", "status": "Deallocating"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/azure/resources")
def azure_resources():
    try:
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        resource_group  = os.getenv("AZURE_RESOURCE_GROUP")

        credential       = AzureCliCredential()
        resource_client  = ResourceManagementClient(credential, subscription_id)

        resources = resource_client.resources.list_by_resource_group(resource_group)
        result = [{"name": r.name, "type": r.type.split("/")[-1]} for r in resources]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
