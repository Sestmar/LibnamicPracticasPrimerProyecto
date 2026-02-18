import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Configuración SMTP (Mailtrap para desarrollo)
SMTP_HOST = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
MAIL_FROM = os.getenv("MAIL_FROM", "noreply@libnamicshop.com")


def _build_order_html(user, order) -> str:
    """Construye el HTML del email con el resumen del pedido."""
    
    items_html = ""
    for item in order.items:
        product_name = item.product.name if item.product else f"Producto #{item.product_id}"
        subtotal = item.unit_price * item.quantity
        items_html += f"""
        <tr>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f0f0f0;">{product_name}</td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f0f0f0; text-align: center;">{item.quantity}</td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f0f0f0; text-align: right;">{item.unit_price:.2f} €</td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f0f0f0; text-align: right;">{subtotal:.2f} €</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0; padding:0; font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #f4f6f9;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; margin-top: 20px;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #2c3e50, #3498db); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">LibnamicShop</h1>
                <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0;">Confirmación de Pedido</p>
            </div>

            <div style="padding: 30px;">
                <p style="color: #2c3e50; font-size: 16px;">
                    ¡Hola <strong>{user.first_name}</strong>! 👋
                </p>
                <p style="color: #555;">
                    Tu pedido <strong>#{order.id}</strong> ha sido registrado correctamente. 
                    Aquí tienes el resumen:
                </p>

                <!-- Tabla de productos -->
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 12px 16px; text-align: left; font-size: 12px; text-transform: uppercase; color: #718096;">Producto</th>
                            <th style="padding: 12px 16px; text-align: center; font-size: 12px; text-transform: uppercase; color: #718096;">Cant.</th>
                            <th style="padding: 12px 16px; text-align: right; font-size: 12px; text-transform: uppercase; color: #718096;">Precio</th>
                            <th style="padding: 12px 16px; text-align: right; font-size: 12px; text-transform: uppercase; color: #718096;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>

                <!-- Total -->
                <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; text-align: right; margin-top: 10px;">
                    <span style="font-size: 18px; font-weight: 800; color: #2c3e50;">
                        Total: {order.total_price:.2f} €
                    </span>
                </div>

                <!-- Estado -->
                <div style="margin-top: 20px; padding: 16px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #f39c12;">
                    <p style="margin: 0; color: #856404;">
                        📦 <strong>Estado:</strong> {order.status} — Te notificaremos cuando sea enviado.
                    </p>
                </div>
            </div>

            <!-- Footer -->
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #eee;">
                <p style="margin: 0; color: #a0aec0; font-size: 12px;">
                    LibnamicShop — Sistema de Gestión de Inventario
                </p>
                <p style="margin: 4px 0 0; color: #cbd5e0; font-size: 11px;">
                    Este email fue generado automáticamente. No respondas a este mensaje.
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def send_order_confirmation(user, order):
    """
    Envía un email de confirmación de pedido al usuario.
    Si las credenciales SMTP no están configuradas, simplemente logea y no falla.
    """
    if not SMTP_USER or not SMTP_PASS:
        print(f"[EMAIL] SMTP no configurado. Skipping email para pedido #{order.id} ({user.email})")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"✅ Pedido #{order.id} confirmado — LibnamicShop"
        msg["From"] = MAIL_FROM
        msg["To"] = user.email

        html_content = _build_order_html(user, order)
        msg.attach(MIMEText(html_content, "html"))

        print(f"[EMAIL] Conectando a {SMTP_HOST}:{SMTP_PORT} con user={SMTP_USER[:4]}***")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(MAIL_FROM, user.email, msg.as_string())
        server.quit()

        print(f"[EMAIL] ✅ Email enviado a {user.email} para pedido #{order.id}")
        return True

    except Exception as e:
        print(f"[EMAIL] ❌ Error enviando email: {e}")
        return False
