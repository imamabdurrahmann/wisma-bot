"""Wisma Bot - Main entry point for WhatsApp booking bot."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import our modules
from db import init_db
from handlers import WismaHandler
from config import OWNER_NUMBER


class WismaBot:
    """Main bot class for Wisma Bot."""

    def __init__(self):
        self.handler = WismaHandler()
        self.owner_number = OWNER_NUMBER
        self.session_file = Path("session.json")
        self.running = False

    async def start(self):
        """Start the bot and initialize connections."""
        logger.info("=" * 50)
        logger.info("🚀 Starting Wisma Bot...")
        logger.info("=" * 50)

        # Initialize database
        init_db()
        logger.info("✅ Database initialized")

        # Load session
        await self.load_session()
        logger.info(f"✅ Owner number: {self.owner_number}")

        # Setup WhatsApp connection
        await self.setup_whatsapp()

        self.running = True

        # Start the main loop
        if self.is_test_mode():
            await self.run_test_mode()
        else:
            await self.run_wa_mode()

    async def load_session(self):
        """Load or validate session data."""
        if self.session_file.exists():
            logger.info("📁 Session file found")
        else:
            logger.info("📁 No session file - will need QR code scan")

    async def setup_whatsapp(self):
        """Setup WhatsApp connection.

        This is a placeholder for actual WhatsApp integration.
        For Termux/HP Android, you can use:
        - wa-js (JavaScript library via Node.js)
        - WhatsApp Web via browser automation
        - WhatsApp Business API
        - Third-party services

        For testing, set TEST_MODE=1 environment variable
        or use the test mode interface.
        """
        if self.is_test_mode():
            logger.info("📋 TEST MODE enabled - WhatsApp integration skipped")
            return

        # Placeholder for actual WhatsApp connection
        # Example with wa-js (Node.js):
        #
        # import subprocess
        # result = subprocess.run(['node', 'whatsapp.js'], ...)
        #
        # Or with a Python library if available:
        # from whatsapp import Client
        # self.wa_client = Client(session=self.session_file)

        logger.info("⚠️ WhatsApp integration not yet configured")
        logger.info("   Set TEST_MODE=1 to run in test mode")
        logger.info("   Or integrate with actual WhatsApp library")

    def is_test_mode(self) -> bool:
        """Check if running in test mode."""
        return os.environ.get("TEST_MODE", "0") == "1" or "--test" in sys.argv

    async def run_test_mode(self):
        """Run in interactive test mode for manual testing."""
        print("\n" + "=" * 50)
        print("🧪 TEST MODE - Interactive Message Tester")
        print("=" * 50)
        print("Type your messages below to test the bot.\n")
        print("Commands:")
        print("  exit  - Quit the bot")
        print("  clear - Clear the screen")
        print("  menu  - Show main menu")
        print("  book  - Start booking flow")
        print("-" * 50 + "\n")

        while self.running:
            try:
                msg = input("You: ").strip()
                if not msg:
                    continue

                # Handle special commands
                if msg.lower() == "exit":
                    break
                if msg.lower() == "clear":
                    os.system("cls" if os.name == "nt" else "clear")
                    continue

                # Process message through handler
                response = self.handler.handle_message("test_user", msg)
                if response:
                    print(f"Bot: {response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Shutting down...")
                break
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                print(f"Error: {e}\n")

        print("Bot stopped. Goodbye!")

    async def run_wa_mode(self):
        """Run with actual WhatsApp integration.

        This method would be called when WhatsApp is properly configured.
        It handles the message loop for real WhatsApp messages.
        """
        logger.info("📱 WhatsApp mode - listening for messages...")

        # Placeholder for actual WhatsApp message loop
        # Example structure:
        #
        # async def on_message(sender, message):
        #     response = self.handler.handle_message(sender, message)
        #     if response:
        #         await self.send_message(sender, response)
        #
        # while self.running:
        #     await asyncio.sleep(1)
        #     # Check for new messages via WhatsApp API
        #     # Call on_message() for each new message

        logger.info("⚠️ WhatsApp integration not implemented")
        logger.info("   Use TEST_MODE=1 or --test to run in test mode")

        # Keep running but do nothing
        while self.running:
            await asyncio.sleep(1)

    async def send_message(self, recipient: str, message: str):
        """Send a message via WhatsApp.

        Args:
            recipient: Phone number to send to
            message: Message text to send
        """
        # Placeholder - would integrate with actual WhatsApp API
        logger.info(f"📤 Would send to {recipient}: {message[:50]}...")
        pass

    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("🛑 Shutting down...")
        self.running = False


async def main():
    """Main entry point."""
    bot = WismaBot()

    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        await bot.shutdown()


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        sys.exit(1)

    # Run the bot
    asyncio.run(main())