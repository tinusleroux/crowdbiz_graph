#!/usr/bin/env python3
"""
CrowdBiz Graph - Single Entry Point
Provides unified access to all application modes and utilities.
"""
import sys
import subprocess
import os

def print_usage():
    """Print usage information."""
    print("""
CrowdBiz Graph - Sports Industry Professional Network

Usage: python run.py [command]

Commands:
  streamlit     Start the Streamlit web application
  api          Start the FastAPI service (optional)
  refresh      Refresh the database summary tables
  checks       Run all validation and compliance checks
  tests        Run the test suite
  setup        Initial setup and configuration
  help         Show this help message

Examples:
  python run.py streamlit    # Start the main application
  python run.py refresh     # Update summary tables for the UI
  python run.py checks      # Validate privacy compliance and code quality
  python run.py tests       # Run all tests
""")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['help', '--help', '-h']:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "streamlit":
            # Start the main Streamlit application with proper Python path
            import os
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()
            subprocess.run(["streamlit", "run", "app/main.py", "--server.port=8501"], env=env)
            
        elif command == "api":
            # Start the optional FastAPI service
            subprocess.run(["python", "app/api/main.py"])
            
        elif command == "refresh":
            # Refresh the summary tables
            print("🔄 Refreshing summary tables...")
            subprocess.run(["python", "refresh_summary_tables.py"])
            print("✅ Summary tables refreshed successfully.")
            
        elif command == "checks":
            # Run all validation checks
            if os.path.exists(".ai_checks/run_all_checks.py"):
                subprocess.run(["python", ".ai_checks/run_all_checks.py"])
            else:
                print("Validation checks not yet implemented. Run after migration completion.")
                
        elif command == "tests":
            # Run the test suite
            if os.path.exists("tests/"):
                subprocess.run(["python", "-m", "pytest", "tests/", "-v"])
            else:
                print("Tests not yet implemented. Run after migration completion.")
                
        elif command == "setup":
            # Initial setup
            print("Running initial setup...")
            print("1. Checking Python dependencies...")
            subprocess.run(["pip", "install", "-r", "requirements.txt"])
            print("2. Setup complete!")
            
        else:
            print(f"Unknown command: {command}")
            print_usage()
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except FileNotFoundError as e:
        print(f"Error: Required file not found - {e}")
        print("Make sure you're running from the crowdbiz_db directory")
    except Exception as e:
        print(f"Error running command '{command}': {e}")

if __name__ == "__main__":
    main()
