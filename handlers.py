"""Message handling logic for Wisma Bot WhatsApp bot."""

from datetime import datetime, timedelta
from db import init_db, get_available_rooms, add_booking, get_pending_booking_by_guest, confirm_booking, cancel_booking
from templates import menu_message, availability_message, prices_message, booking_form_message, booking_confirmation, owner_notification, booking_approved, booking_cancelled, format_price
from config import OWNER_NUMBER, ROOMS


class WismaHandler:
    """Handler for processing incoming WhatsApp messages."""

    def __init__(self):
        """Initialize handler with empty state."""
        self.state = {}  # {sender: {"step": "name", "data": {}}}
        self.owner_number = OWNER_NUMBER

    def reset_state(self, sender: str) -> None:
        """Reset state for a sender if exists."""
        if sender in self.state:
            del self.state[sender]

    def is_owner(self, sender: str) -> bool:
        """Check if sender is the owner.

        Handles format with/without + prefix.
        """
        # Normalize sender number (remove + if present)
        normalized_sender = sender.lstrip("+")
        normalized_owner = self.owner_number.lstrip("+")
        return normalized_sender == normalized_owner

    def handle_message(self, sender: str, message: str) -> str | None:
        """Handle incoming message and return response.

        Args:
            sender: Sender's phone number
            message: Incoming message text

        Returns:
            Response message string or None
        """
        msg = message.strip().upper()

        # Handle owner commands
        if self.is_owner(sender):
            if msg.startswith("/APPROVE "):
                booking_id = msg.replace("/APPROVE ", "").strip()
                return self.handle_confirm(booking_id)
            if msg.startswith("/CANCEL "):
                booking_id = msg.replace("/CANCEL ", "").strip()
                return self.handle_cancel(booking_id)

        # Handle in-progress booking state first
        if sender in self.state:
            return self.handle_booking_input(sender, message)

        # Handle main menu commands (only when not in booking flow)
        if msg in ("1", "CEK", "CEK KETERSEDIAAN"):
            return self.handle_availability()
        if msg in ("2", "BOOKING"):
            return self.handle_booking_start(sender)
        if msg in ("3", "HARGA"):
            return self.handle_prices()
        if msg in ("4", "CONTACT", "KONTAK", "KONTAK PEMILIK"):
            return self.handle_contact_owner()
        if msg == "BATAL":
            self.reset_state(sender)
            return "Booking dibatalkan. Kembali ke menu utama.\n\n" + menu_message()
        if msg == "MENU":
            self.reset_state(sender)
            return menu_message()

        # Default: show menu
        return menu_message()

    def handle_availability(self) -> str:
        """Handle availability check request."""
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        available = get_available_rooms(today, tomorrow)
        return availability_message(available)

    def handle_booking_start(self, sender: str) -> str:
        """Start booking flow for a sender."""
        self.state[sender] = {"step": "name", "data": {}}
        return (
            "*BOOKING KAMAR*\n\n"
            "Silakan isi data booking:\n\n"
            "Ketik *nama lengkap* Anda\n\n"
            "(untuk batal, ketik *BATAL*)"
        )

    def handle_prices(self) -> str:
        """Handle price list request."""
        return prices_message()

    def handle_contact_owner(self) -> str:
        """Handle contact owner request."""
        owner_number = self.owner_number.lstrip("+")
        return f"Hubungi pemilik: wa.me/{owner_number}"

    def handle_booking_input(self, sender: str, msg: str) -> str:
        """Handle multi-step booking flow.

        Args:
            sender: Sender's phone number
            msg: Input message

        Returns:
            Next prompt or confirmation message
        """
        step = self.state[sender]["step"]
        data = self.state[sender]["data"]

        if step == "name":
            # Store name and ask for date
            data["name"] = msg.strip()
            self.state[sender] = {"step": "date", "data": data}
            return (
                "*Tanggal Check-in*\n\n"
                "Masukkan tanggal (format: DD/MM/YYYY)\n"
                "Contoh: 15/05/2026\n\n"
                "(untuk batal, ketik *BATAL*)"
            )

        if step == "date":
            # Validate date format
            if not self.validate_date(msg):
                return (
                    "Format tanggal salah!\n\n"
                    "Gunakan format: DD/MM/YYYY\n"
                    "Contoh: 15/05/2026"
                )
            check_in = self.parse_date(msg)
            data["check_in"] = check_in.strftime("%Y-%m-%d")
            self.state[sender] = {"step": "nights", "data": data}
            return (
                "*Jumlah Malam*\n\n"
                "Berapa malam Anda akan menginap?\n"
                "Ketik angka saja (contoh: 2)\n\n"
                "(untuk batal, ketik *BATAL*)"
            )

        if step == "nights":
            # Validate nights
            try:
                nights = int(msg.strip())
                if nights <= 0:
                    return "Jumlah malam harus lebih dari 0. Masukkan angka yang valid."
            except ValueError:
                return "Format salah. Masukkan angka saja (contoh: 2)"

            data["nights"] = nights
            # Calculate check_out
            check_in = datetime.strptime(data["check_in"], "%Y-%m-%d")
            check_out = check_in + timedelta(days=nights)
            data["check_out"] = check_out.strftime("%Y-%m-%d")

            self.state[sender] = {"step": "room", "data": data}
            return (
                "*Pilih Kamar*\n\n"
                f"Tersedia untuk {data['check_in']} s/d {data['check_out']}:\n\n"
                f"{self.get_room_list()}\n\n"
                "Ketik kode kamar (contoh: 1A)\n\n"
                "(untuk batal, ketik *BATAL*)"
            )

        if step == "room":
            room_code = msg.strip().upper()
            # Validate room code exists
            room_info = next((r for r in ROOMS if r["code"] == room_code), None)
            if not room_info:
                return (
                    f"Kamar '{room_code}' tidak ditemukan.\n\n"
                    f"{self.get_room_list()}\n\n"
                    "Ketik kode kamar yang valid."
                )

            # Check availability
            available = get_available_rooms(data["check_in"], data["check_out"])
            if room_code not in available:
                return (
                    f"Maaf, Kamar {room_code} tidak tersedia untuk tanggal tersebut.\n\n"
                    f"Tersedia: {', '.join(available) if available else 'tidak ada'}\n\n"
                    "Pilih kamar lain atau ketik *BATAL* untuk membatalkan."
                )

            # Add booking
            booking_id = add_booking(
                data["name"],
                room_code,
                data["check_in"],
                data["check_out"]
            )

            # Clear state
            self.reset_state(sender)

            # Get room price for confirmation
            price_per_night = room_info["price"]

            # Generate confirmation for guest
            confirmation = booking_confirmation(
                data["name"],
                room_code,
                data["check_in"],
                data["check_out"],
                data["nights"],
                price_per_night
            )

            # Notify owner
            owner_msg = owner_notification(
                booking_id,
                data["name"],
                room_code,
                data["check_in"],
                data["check_out"],
                data["nights"]
            )

            # Return both messages (owner notification would be sent separately in real implementation)
            return confirmation + "\n\n---\n\n[Notifikasi ke pemilik telah dikirim]"

        return menu_message()

    def validate_date(self, date_str: str) -> bool:
        """Validate date string format DD/MM/YYYY and not in the past.

        Args:
            date_str: Date string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = self.parse_date(date_str)
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return parsed >= today
        except ValueError:
            return False

    def parse_date(self, date_str: str) -> datetime:
        """Parse date string in DD/MM/YYYY format.

        Args:
            date_str: Date string to parse

        Returns:
            datetime object
        """
        return datetime.strptime(date_str.strip(), "%d/%m/%Y")

    def get_room_list(self) -> str:
        """Get formatted list of rooms for selection.

        Returns:
            Formatted room list string
        """
        lines = []
        for room in ROOMS:
            emoji = "❄️" if room["type"] == "AC" else "🌬️"
            price = format_price(room["price"])
            lines.append(f"{emoji} Kamar {room['code']}: {price}/malam")
        return "\n".join(lines)

    def handle_confirm(self, booking_id_or_name: str) -> str:
        """Handle booking approval by owner.

        Args:
            booking_id_or_name: Booking ID or guest name

        Returns:
            Result message
        """
        # Try to parse as ID first
        try:
            booking_id = int(booking_id_or_name)
            # Get booking by ID directly
            conn = __import__('db').get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, guest_name, room_code FROM bookings WHERE id = ? AND status = 'pending'",
                (booking_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return f"Booking #{booking_id} tidak ditemukan atau sudah diproses."
            guest_name = dict(row)["guest_name"]
            room_code = dict(row)["room_code"]
            success = confirm_booking(booking_id)
        except ValueError:
            # Try to find by guest name
            booking = get_pending_booking_by_guest(booking_id_or_name)
            if not booking:
                return f"Booking untuk '{booking_id_or_name}' tidak ditemukan."
            guest_name = booking["guest_name"]
            room_code = booking["room_code"]
            success = confirm_booking(booking["id"])

        if success:
            return (
                f"✅ Booking #{booking_id if 'booking_id' in dir() else booking['id']} *DITERIMA*\n\n"
                f"Tamu: {guest_name}\n"
                f"Kamar: {room_code}\n\n"
                f"[Notifikasi ke tamu telah dikirim]"
            )
        return "Gagal mengkonfirmasi booking."

    def handle_cancel(self, booking_id_or_name: str) -> str:
        """Handle booking cancellation by owner.

        Args:
            booking_id_or_name: Booking ID or guest name

        Returns:
            Result message
        """
        # Try to parse as ID first
        try:
            booking_id = int(booking_id_or_name)
            # Get booking by ID directly
            conn = __import__('db').get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, guest_name FROM bookings WHERE id = ?",
                (booking_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return f"Booking #{booking_id} tidak ditemukan."
            guest_name = dict(row)["guest_name"]
            success = cancel_booking(booking_id)
        except ValueError:
            # Try to find by guest name
            booking = get_pending_booking_by_guest(booking_id_or_name)
            if not booking:
                return f"Booking untuk '{booking_id_or_name}' tidak ditemukan."
            guest_name = booking["guest_name"]
            success = cancel_booking(booking["id"])

        if success:
            return (
                f"❌ Booking *DIBATALKAN*\n\n"
                f"Tamu: {guest_name}\n\n"
                f"[Notifikasi ke tamu telah dikirim]"
            )
        return "Gagal membatalkan booking."
