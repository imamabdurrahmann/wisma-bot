"""Message templates for Wisma Bot WhatsApp responses."""

from config import ROOMS
from datetime import date


def format_price(amount: int) -> str:
    """Format price with Indonesian thousand separator.

    Args:
        amount: Price in rupiah

    Returns:
        Formatted price string (e.g., "Rp300.000")
    """
    return f"Rp{amount:,}".replace(",", ".")


def menu_message() -> str:
    """Return main menu with 4 options.

    Returns:
        WhatsApp-formatted menu message
    """
    return (
        "*MENU WISMA BOT*\n\n"
        "Silakan pilih:\n\n"
        "1️⃣ *CEK KETERSEDIAAN*\n"
        "   Lihat kamar yang tersedia\n\n"
        "2️⃣ *HARGA KAMAR*\n"
        "   Lihat daftar harga\n\n"
        "3️⃣ *BOOKING KAMAR*\n"
        "   Ajukan pemesanan\n\n"
        "4️⃣ *CANCEL BOOKING*\n"
        "   Batalkan pemesanan\n\n"
        "_Balas dengan angka atau ketik command_"
    )


def availability_message(available_rooms: list) -> str:
    """Format availability message with room list.

    Args:
        available_rooms: List of available room codes

    Returns:
        Formatted availability message
    """
    if not available_rooms:
        return "Maaf, semua kamar sedang penuh"

    # Build room info mapping from ROOMS config
    room_info = {room["code"]: room for room in ROOMS}

    # Group by type
    ac_rooms = []
    non_ac_rooms = []

    for code in sorted(available_rooms):
        if code in room_info:
            if room_info[code]["type"] == "AC":
                ac_rooms.append(code)
            else:
                non_ac_rooms.append(code)

    lines = ["*KAMAR TERSEDIA*\n"]

    if ac_rooms:
        lines.append("❄️ *AC Rooms:*")
        lines.append("   " + ", ".join(ac_rooms))
        lines.append("")

    if non_ac_rooms:
        lines.append("🌬️ *Non-AC Rooms:*")
        lines.append("   " + ", ".join(non_ac_rooms))
        lines.append("")

    lines.append("_Untuk booking, ketik *BOOKING*_")
    return "\n".join(lines)


def prices_message() -> str:
    """Return price list for all rooms.

    Returns:
        Formatted price list message
    """
    # Group by type
    ac_rooms = []
    non_ac_rooms = []

    for room in ROOMS:
        if room["type"] == "AC":
            ac_rooms.append(room)
        else:
            non_ac_rooms.append(room)

    lines = ["*DAFTAR HARGA KAMAR*\n"]

    if ac_rooms:
        lines.append("❄️ *AC Rooms:*")
        for room in sorted(ac_rooms, key=lambda x: x["price"], reverse=True):
            lines.append(f"   Kamar {room['code']}: {format_price(room['price'])}/malam")
        lines.append("")

    if non_ac_rooms:
        lines.append("🌬️ *Non-AC Rooms:*")
        for room in sorted(non_ac_rooms, key=lambda x: x["price"], reverse=True):
            lines.append(f"   Kamar {room['code']}: {format_price(room['price'])}/malam")

    lines.append("")
    lines.append("_Untuk menginap lama, bisa nego.")
    lines.append("Hubungi pemilik langsung!_")

    return "\n".join(lines)


def booking_form_message() -> str:
    """Return booking form format instructions.

    Returns:
        Formatted booking form message
    """
    return (
        "*FORM BOOKING KAMAR*\n\n"
        "Silakan isi format berikut:\n\n"
        "NAMA: [Nama lengkap]\n"
        "TANGGAL: [YYYY-MM-DD]\n"
        "LAMA: [Jumlah malam]\n"
        "KAMAR: [Kode kamar]\n\n"
        "*Contoh:*\n"
        "NAMA: Budi Santoso\n"
        "TANGGAL: 2026-05-15\n"
        "LAMA: 2\n"
        "KAMAR: 1A\n\n"
        "_Untuk batal, ketik *BATAL*_"
    )


def booking_confirmation(guest_name, room_code, check_in, check_out, nights, price_per_night) -> str:
    """Format booking confirmation message.

    Args:
        guest_name: Guest name
        room_code: Room code
        check_in: Check-in date string (YYYY-MM-DD)
        check_out: Check-out date string (YYYY-MM-DD)
        nights: Number of nights
        price_per_night: Price per night

    Returns:
        Formatted confirmation message
    """
    total_price = nights * price_per_night

    # Determine room type emoji
    room_type = next((r["type"] for r in ROOMS if r["code"] == room_code), "")
    emoji = "❄️" if room_type == "AC" else "🌬️"

    return (
        f"*BOOKING DITERIMA*\n\n"
        f"{emoji} *Kamar {room_code}*\n\n"
        f"Nama: {guest_name}\n"
        f"Check-in: {check_in}\n"
        f"Check-out: {check_out}\n"
        f"Lama: {nights} malam\n\n"
        f"Harga/malam: {format_price(price_per_night)}\n"
        f"*Estimasi Total: {format_price(total_price)}*\n\n"
        f"Status: *Menunggu konfirmasi pemilik*\n\n"
        "_Anda akan mendapat notifikasi setelah pemilik mengkonfirmasi booking._"
    )


def owner_notification(booking_id, guest_name, room_code, check_in, check_out, nights) -> str:
    """Format booking notification for owner.

    Args:
        booking_id: Booking ID
        guest_name: Guest name
        room_code: Room code
        check_in: Check-in date string (YYYY-MM-DD)
        check_out: Check-out date string (YYYY-MM-DD)
        nights: Number of nights

    Returns:
        Formatted notification message for owner
    """
    # Get room price
    room_info = next((r for r in ROOMS if r["code"] == room_code), None)
    price_per_night = room_info["price"] if room_info else 0
    room_type = room_info["type"] if room_info else ""

    emoji = "❄️" if room_type == "AC" else "🌬️"

    return (
        f"*📋 BOOKING BARU*\n\n"
        f"ID: #{booking_id}\n\n"
        f"Tamu: {guest_name}\n"
        f"{emoji} Kamar {room_code} ({room_type})\n"
        f"Check-in: {check_in}\n"
        f"Check-out: {check_out}\n"
        f"Lama: {nights} malam\n\n"
        f"Estimasi: {format_price(nights * price_per_night)}\n\n"
        f"*Action:*\n"
        f"✅ /approve {booking_id} - Terima\n"
        f"❌ /cancel {booking_id} - Tolak"
    )


def booking_approved(guest_name, room_code) -> str:
    """Format booking approved message for guest.

    Args:
        guest_name: Guest name
        room_code: Room code

    Returns:
        Formatted approval message
    """
    # Determine room type emoji
    room_type = next((r["type"] for r in ROOMS if r["code"] == room_code), "")
    emoji = "❄️" if room_type == "AC" else "🌬️"

    return (
        f"*✅ BOOKING DITERIMA*\n\n"
        f"Hai {guest_name}!\n\n"
        f"{emoji} Kamar {room_code} Anda telah *dikonfirmasi*.\n\n"
        f"Selamat menikmati tinggal di Wisma!\n\n"
        f"_Jika ada pertanyaan, hubungi pemilik._"
    )


def booking_cancelled(guest_name) -> str:
    """Format booking cancelled message for guest.

    Args:
        guest_name: Guest name

    Returns:
        Formatted cancellation message
    """
    return (
        f"*❌ BOOKING DIBATALKAN*\n\n"
        f"Hai {guest_name},\n\n"
        f"Booking Anda telah *dibatalkan*.\n\n"
        f"Jika ingin booking ulang, silakan ketik *BOOKING*.\n\n"
        f"_Mohon maaf atas ketidaknyamanannya._"
    )