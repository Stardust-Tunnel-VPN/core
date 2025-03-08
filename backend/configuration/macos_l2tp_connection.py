async def create_macos_l2tp_service(
    server_ip: str,
    service_name: str = "MyL2TP",
    psk: str = "vpn",
    username: str = "vpn",
    password: str = "vpn",
) -> None:
    """
    Create an L2TP/IPSec VPN profile on macOS by installing a .mobileconfig.
    This requires 'sudo' privileges.
    The user might be prompted for a password or a GUI confirmation.

    In a real scenario, we build the .mobileconfig with the needed XML/plist content,
    then run `profiles install`.
    """
    try:
        unique_id = str(uuid.uuid4())
        config_path = f"/tmp/{service_name}_{unique_id}.mobileconfig"

        # This is a minimal example with placeholders for psk, user, pass
        # In reality, you'd do proper base64 encoding, or store password differently
        profile_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC ...
<plist version="1.0">
<dict>
  <key>PayloadType</key><string>Configuration</string>
  <key>PayloadIdentifier</key><string>com.example.{service_name}</string>
  <key>PayloadUUID</key><string>{unique_id}</string>
  <key>PayloadVersion</key><integer>1</integer>
  <key>PayloadContent</key>
  <array>
    <dict>
      <key>PayloadType</key>
      <string>com.apple.vpn.managed</string>
      <key>UserDefinedName</key>
      <string>{service_name}</string>
      <key>VPNType</key>
      <string>L2TP</string>
      <key>VPNSubType</key>
      <string>L2TP</string>
      <key>RemoteAddress</key>
      <string>{server_ip}</string>
      <key>IPSec</key>
      <dict>
        <key>AuthenticationMethod</key><string>SharedSecret</string>
        <key>SharedSecret</key><data>{psk.encode('utf-8').hex()}</data>
      </dict>
      <key>PPP</key>
      <dict>
        <key>AuthName</key><string>{username}</string>
        <key>AuthPassword</key><string>{password}</string>
      </dict>
    </dict>
  </array>
</dict>
</plist>
"""

        with open(config_path, "w") as f:
            f.write(profile_plist)

        cmd = ["sudo", "profiles", "install", "-type", "configuration", "-path", config_path]
        logger.info(f"Installing macOS L2TP profile via: {cmd}")
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            err = stderr.decode()
            raise RuntimeError(f"Failed to install mobileconfig: {err}")

        logger.info(
            f"Profile installed for {service_name}. You can now connect with scutil --nc start {service_name}."
        )
        # Optionally remove the file
        os.remove(config_path)

    except Exception as exc:
        logger.error(f"create_macos_l2tp_service failed: {exc}")
        raise
