"""
E-Commerce Platform Launcher
Runs the backend server in the background with a system tray icon.
"""
import sys
import os
import subprocess
import threading
import webbrowser
import time
import socket
import atexit

# Add the current directory to path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

# Lock file to prevent multiple instances
LOCK_FILE = os.path.join(BASE_DIR, ".ecommerce_app.lock")

def check_single_instance():
    """Ensure only one instance is running"""
    if os.path.exists(LOCK_FILE):
        # Check if the process is still running by trying to connect to the port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 8001))
            sock.close()
            if result == 0:
                print("E-Commerce App is already running!")
                print("Check your system tray for the icon.")
                webbrowser.open("http://localhost:8080/index.html")
                sys.exit(0)
        except:
            pass
        # Remove stale lock file
        try:
            os.remove(LOCK_FILE)
        except:
            pass
    
    # Create lock file
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def cleanup_lock():
    """Remove lock file on exit"""
    try:
        os.remove(LOCK_FILE)
    except:
        pass

# Register cleanup
atexit.register(cleanup_lock)

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pystray", "Pillow"])
    import pystray
    from PIL import Image, ImageDraw


class ECommerceServer:
    def __init__(self):
        self.server_process = None
        self.is_running = False
        self.icon = None
        self.port = 8001
        self.frontend_port = 8080
        self.frontend_process = None
        
    def create_icon_image(self, color="green"):
        """Create a simple colored circle icon"""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw outer circle (border)
        draw.ellipse([2, 2, size-2, size-2], fill='white', outline='black')
        
        # Draw inner circle (status color)
        if color == "green":
            fill_color = (76, 175, 80)  # Green - running
        elif color == "red":
            fill_color = (244, 67, 54)  # Red - stopped
        else:
            fill_color = (255, 193, 7)  # Yellow - starting
            
        draw.ellipse([8, 8, size-8, size-8], fill=fill_color)
        
        # Draw a simple "E" for E-Commerce
        draw.text((22, 18), "E", fill='white')
        
        return image
    
    def update_icon(self, status="running"):
        """Update the tray icon based on server status"""
        if self.icon:
            if status == "running":
                self.icon.icon = self.create_icon_image("green")
                self.icon.title = "E-Commerce Server (Running on port {})".format(self.port)
            elif status == "stopped":
                self.icon.icon = self.create_icon_image("red")
                self.icon.title = "E-Commerce Server (Stopped)"
            else:
                self.icon.icon = self.create_icon_image("yellow")
                self.icon.title = "E-Commerce Server (Starting...)"
    
    def check_database(self):
        """Initialize database if it doesn't exist"""
        db_path = os.path.join(BASE_DIR, "database.db")
        if not os.path.exists(db_path):
            print("Database not found. Initializing...")
            try:
                init_script = os.path.join(BASE_DIR, "backend", "init_db.py")
                subprocess.run([sys.executable, init_script], 
                             cwd=BASE_DIR, check=True)
                print("Database initialized successfully!")
            except Exception as e:
                print(f"Error initializing database: {e}")
                return False
        return True
    
    def start_server(self):
        """Start the backend server"""
        if self.is_running:
            return
        
        self.update_icon("starting")
        
        # Check/initialize database
        if not self.check_database():
            self.update_icon("stopped")
            return
        
        try:
            # Start uvicorn server
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "backend.main:app", 
                 "--host", "0.0.0.0", "--port", str(self.port)],
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # Wait a moment for server to start
            time.sleep(2)
            
            if self.server_process.poll() is None:
                self.is_running = True
                self.update_icon("running")
                print(f"Server started on port {self.port}")
            else:
                self.update_icon("stopped")
                print("Server failed to start")
                
        except Exception as e:
            print(f"Error starting server: {e}")
            self.update_icon("stopped")
    
    def stop_server(self):
        """Stop the backend server"""
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            self.frontend_process = None
            
        self.is_running = False
        self.update_icon("stopped")
        print("Server stopped")
    
    def start_frontend_server(self):
        """Start the frontend HTTP server"""
        frontend_dir = os.path.join(BASE_DIR, "frontend")
        try:
            self.frontend_process = subprocess.Popen(
                [sys.executable, "-m", "http.server", str(self.frontend_port)],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            time.sleep(1)
            print(f"Frontend server started on port {self.frontend_port}")
        except Exception as e:
            print(f"Error starting frontend server: {e}")
    
    def open_browser(self, item=None):
        """Open the application in browser"""
        url = f"http://localhost:{self.frontend_port}/index.html"
        webbrowser.open(url)
    
    def open_api_docs(self, item=None):
        """Open API documentation"""
        url = f"http://localhost:{self.port}/docs"
        webbrowser.open(url)
    
    def restart_server(self, item=None):
        """Restart the server"""
        self.stop_server()
        time.sleep(1)
        self.start_server()
        self.start_frontend_server()
    
    def quit_app(self, item=None):
        """Quit the application"""
        self.stop_server()
        if self.icon:
            self.icon.stop()
    
    def create_menu(self):
        """Create the system tray menu"""
        return pystray.Menu(
            pystray.MenuItem("Open E-Commerce App", self.open_browser, default=True),
            pystray.MenuItem("Open API Docs", self.open_api_docs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Restart Server", self.restart_server),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit_app)
        )
    
    def run(self):
        """Main entry point"""
        # Start servers in background thread
        def startup():
            time.sleep(1)  # Wait for icon to be ready
            self.start_server()
            self.start_frontend_server()
            time.sleep(1)
            self.open_browser()
        
        startup_thread = threading.Thread(target=startup, daemon=True)
        startup_thread.start()
        
        # Create and run system tray icon
        self.icon = pystray.Icon(
            "ecommerce",
            self.create_icon_image("yellow"),
            "E-Commerce Server (Starting...)",
            self.create_menu()
        )
        
        self.icon.run()


def main():
    print("=" * 50)
    print("E-Commerce Platform Launcher")
    print("=" * 50)
    
    # Prevent multiple instances
    check_single_instance()
    
    server = ECommerceServer()
    
    try:
        server.run()
    except KeyboardInterrupt:
        server.quit_app()
    finally:
        cleanup_lock()


if __name__ == "__main__":
    main()

