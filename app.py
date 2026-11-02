#!/usr/bin/env python3
"""
Linktree Clone Web Application with Admin Panel
Built with Python 3, Tornado & SQLite.
"""

import os
import sys
import json
import time
import argparse
import secrets
import tornado.ioloop
import tornado.web
import tornado.escape
import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("linktree_admin_user")
        if user_id:
            try:
                user = database.get_user_by_id(int(user_id.decode("utf-8")))
                return user
            except Exception:
                return None
        return None

    def render(self, template_name, **kwargs):
        kwargs["json_encode"] = json.dumps
        kwargs["round"] = round
        kwargs["max"] = max
        kwargs["min"] = min
        super().render(template_name, **kwargs)

    def write_json(self, data, status_code=200):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code)
        self.write(json.dumps(data))

    def get_json_body(self):
        try:
            return json.loads(self.request.body.decode("utf-8"))
        except Exception:
            return {}

class PublicProfileHandler(BaseHandler):
    def get(self, handle=None):
        profile = database.get_profile()
        is_admin = bool(self.get_current_user())
        
        # In admin live preview mode, show all links
        preview = self.get_argument("preview", "0") == "1"
        only_active = not (preview or is_admin)
        links = database.get_links(only_active=only_active)
        
        self.render(
            "index.html",
            page_title=f"{profile['name']} (@{profile['handle']}) | Linktree",
            page_description=profile.get("bio", "Connect with my links and social media."),
            profile=profile,
            links=links,
            is_admin=is_admin
        )

class ClickRedirectHandler(BaseHandler):
    def get(self, link_id):
        try:
            lid = int(link_id)
        except ValueError:
            self.redirect("/")
            return

        user_agent = self.request.headers.get("User-Agent", "")
        ip_address = self.request.remote_ip or ""
        target_url = database.record_click(lid, user_agent, ip_address)
        
        if target_url:
            self.redirect(target_url, status=302)
        else:
            self.redirect("/")

class LoginHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.redirect("/admin")
            return
        self.render("login.html", page_title="Admin Login | Linktree", page_description="Login Admin", error=None)

    def post(self):
        username = self.get_body_argument("username", "").strip()
        password = self.get_body_argument("password", "").strip()

        user = database.get_user_by_username(username)
        if user and database.verify_password(user["password_hash"], password):
            # Set secure cookie valid for 7 days
            self.set_secure_cookie("linktree_admin_user", str(user["id"]), expires_days=7)
            self.redirect("/admin")
        else:
            self.render(
                "login.html",
                page_title="Admin Login | Linktree",
                page_description="Login Admin",
                error="Username atau password yang dimasukkan salah!"
            )

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("linktree_admin_user")
        self.redirect("/login")

class AdminDashboardHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        profile = database.get_profile()
        links = database.get_links(only_active=False)
        stats = database.get_analytics_summary()
        self.render(
            "admin.html",
            page_title="Dashboard Pengelolaan Link | Linktree Admin",
            page_description="Admin Panel untuk mengatur tautan Linktree",
            profile=profile,
            links=links,
            stats=stats,
            user=self.current_user
        )

# API Handlers
class ApiLinksHandler(BaseHandler):
    def post(self):
        if not self.get_current_user():
            return self.write_json({"success": False, "message": "Unauthorized"}, 401)
        
        data = self.get_json_body()
        title = data.get("title", "").strip()
        url = data.get("url", "").strip()
        subtitle = data.get("subtitle", "").strip()
        icon = data.get("icon", "🔗").strip() or "🔗"
        category = data.get("category", "").strip()
        is_active = int(data.get("is_active", 1))
        is_highlighted = int(data.get("is_highlighted", 0))

        if not title or not url:
            return self.write_json({"success": False, "message": "Judul dan URL wajib diisi"}, 400)

        new_id = database.add_link(title, url, subtitle, icon, category, is_active, is_highlighted)
        return self.write_json({"success": True, "id": new_id, "message": "Link berhasil ditambahkan"})

class ApiLinkDetailHandler(BaseHandler):
    def put(self, link_id):
        if not self.get_current_user():
            return self.write_json({"success": False, "message": "Unauthorized"}, 401)
        
        try:
            lid = int(link_id)
        except ValueError:
            return self.write_json({"success": False, "message": "ID tidak valid"}, 400)

        data = self.get_json_body()
        title = data.get("title", "").strip()
        url = data.get("url", "").strip()
        subtitle = data.get("subtitle", "").strip()
        icon = data.get("icon", "🔗").strip() or "🔗"
        category = data.get("category", "").strip()
        is_active = int(data.get("is_active", 1))
        is_highlighted = int(data.get("is_highlighted", 0))

        if not title or not url:
            return self.write_json({"success": False, "message": "Judul dan URL wajib diisi"}, 400)

        ok = database.update_link(lid, title, url, subtitle, icon, category, is_active, is_highlighted)
        return self.write_json({"success": ok, "message": "Link berhasil diperbarui" if ok else "Gagal memperbarui link"})

    def delete(self, link_id):
        if not self.get_current_user():
            return self.write_json({"success": False, "message": "Unauthorized"}, 401)
        try:
            lid = int(link_id)
        except ValueError:
            return self.write_json({"success": False, "message": "ID tidak valid"}, 400)

        ok = database.delete_link(lid)
        return self.write_json({"success": ok, "message": "Link berhasil dihapus" if ok else "Gagal menghapus link"})

class ApiLinkToggleHandler(BaseHandler):
    def post(self, link_id):
        if not self.get_current_user():
            return self.write_json({"success": False, "message": "Unauthorized"}, 401)
        try:
            lid = int(link_id)
        except ValueError:
            return self.write_json({"success": False, "message": "ID tidak valid"}, 400)

        new_status = database.toggle_link_status(lid)
        if new_status is not None:
            return self.write_json({"success": True, "is_active": new_status})
        return self.write_json({"success": False, "message": "Link tidak ditemukan"}, 404)

class ApiLinksReorderHandler(BaseHandler):
    def post(self):
        if not self.get_current_user():
            return self.write_json({"success": False, "message": "Unauthorized"}, 401)
        data = self.get_json_body()
        ordered_ids = data.get("ordered_ids", [])
        if not isinstance(ordered_ids, list):
            return self.write_json({"success": False, "message": "Format data urutan salah"}, 400)
        
        ok = database.reorder_links(ordered_ids)
        return self.write_json({"success": ok})

class ApiProfileHandler(BaseHandler):
    def post(self):
        if not self.get_current_user():
            return self.write_json({"success": False, "message": "Unauthorized"}, 401)
        
        data = self.get_json_body()
        name = data.get("name", "").strip() or "Aldian Dev"
        handle = data.get("handle", "").strip().lstrip("@") or "aldiandev"
        bio = data.get("bio", "").strip()
        avatar_url = data.get("avatar_url", "").strip()
        try:
            avatar_size = int(data.get("avatar_size", 104))
            avatar_size = max(50, min(avatar_size, 200)) # clamp between 50 and 200
        except (ValueError, TypeError):
            avatar_size = 104
        theme = data.get("theme", "glass")
        socials = data.get("socials", {})
        footer_text = data.get("footer_text", "")
        show_share_button = int(data.get("show_share_button", 1))

        ok = database.update_profile(name, handle, bio, avatar_url, avatar_size, theme, socials, footer_text, show_share_button)
        return self.write_json({"success": ok, "message": "Profil berhasil diperbarui" if ok else "Gagal memperbarui profil"})

class ApiUploadAvatarHandler(BaseHandler):
    def post(self):
        if not self.get_current_user():
            return self.write_json({"success": False, "message": "Unauthorized"}, 401)
        
        if "avatar" not in self.request.files:
            return self.write_json({"success": False, "message": "File gambar tidak ditemukan"}, 400)

        file_obj = self.request.files["avatar"][0]
        original_ext = os.path.splitext(file_obj["filename"])[1].lower()
        if original_ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]:
            original_ext = ".png"

        new_filename = f"avatar_{int(time.time())}{original_ext}"
        destination_path = os.path.join(UPLOAD_DIR, new_filename)

        with open(destination_path, "wb") as f:
            f.write(file_obj["body"])

        avatar_url = f"/static/uploads/{new_filename}"
        return self.write_json({"success": True, "avatar_url": avatar_url})

class ApiUploadIconHandler(BaseHandler):
    def post(self):
        if not self.get_current_user():
            return self.write_json({"success": False, "message": "Unauthorized"}, 401)
        
        if "icon_file" not in self.request.files:
            return self.write_json({"success": False, "message": "File icon tidak ditemukan"}, 400)

        file_obj = self.request.files["icon_file"][0]
        original_ext = os.path.splitext(file_obj["filename"])[1].lower()
        if original_ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".ico"]:
            original_ext = ".png"

        icon_dir = os.path.join(UPLOAD_DIR, "icons")
        os.makedirs(icon_dir, exist_ok=True)

        new_filename = f"icon_{int(time.time())}_{secrets.token_hex(4)}{original_ext}"
        destination_path = os.path.join(icon_dir, new_filename)

        with open(destination_path, "wb") as f:
            f.write(file_obj["body"])

        icon_url = f"/static/uploads/icons/{new_filename}"
        return self.write_json({"success": True, "icon_url": icon_url, "message": "Icon berhasil diunggah"})

class ApiChangePasswordHandler(BaseHandler):
    def post(self):
        user = self.get_current_user()
        if not user:
            return self.write_json({"success": False, "message": "Unauthorized"}, 401)

        data = self.get_json_body()
        current_password = data.get("current_password", "")
        new_password = data.get("new_password", "")

        user_db = database.get_user_by_id(user["id"])
        row = database.get_user_by_username(user_db["username"])
        if not row or not database.verify_password(row["password_hash"], current_password):
            return self.write_json({"success": False, "message": "Password saat ini salah!"}, 400)

        if len(new_password) < 6:
            return self.write_json({"success": False, "message": "Password baru minimal 6 karakter"}, 400)

        ok = database.update_user_password(user["id"], new_password)
        return self.write_json({"success": ok, "message": "Password berhasil diubah" if ok else "Gagal mengubah password"})

def make_app():
    settings = {
        "template_path": TEMPLATE_DIR,
        "static_path": STATIC_DIR,
        "static_url_prefix": "/static/",
        "cookie_secret": "linktree_secret_key_antigravity_2026_super_safe_token",
        "login_url": "/login",
        "debug": False,
        "autoreload": True
    }

    routes = [
        (r"/", PublicProfileHandler),
        (r"/@([a-zA-Z0-9_\-\.]+)", PublicProfileHandler),
        (r"/l/([0-9]+)", ClickRedirectHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/admin", AdminDashboardHandler),
        (r"/api/links", ApiLinksHandler),
        (r"/api/links/([0-9]+)", ApiLinkDetailHandler),
        (r"/api/links/([0-9]+)/toggle", ApiLinkToggleHandler),
        (r"/api/links/reorder", ApiLinksReorderHandler),
        (r"/api/profile", ApiProfileHandler),
        (r"/api/upload-avatar", ApiUploadAvatarHandler),
        (r"/api/upload-icon", ApiUploadIconHandler),
        (r"/api/change-password", ApiChangePasswordHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": STATIC_DIR}),
    ]

    return tornado.web.Application(routes, **settings)

def main():
    parser = argparse.ArgumentParser(description="Linktree Web Application")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    args = parser.parse_args()

    # Initialize Database
    database.init_db()

    app = make_app()
    app.listen(args.port, address=args.host)
    
    print("=" * 60)
    print("🚀 LINKTREE WEB APPLICATION IS RUNNING!")
    print("=" * 60)
    print(f"🌐 Halaman Publik : http://localhost:{args.port}/")
    print(f"⚙️  Admin Panel    : http://localhost:{args.port}/admin")
    print(f"🔑 Akun Default   : Username: admin | Password: admin123")
    print("=" * 60)
    print("Tekan Ctrl+C untuk menghentikan server.")
    
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
