import pandas as pd
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import glob

# Configuración del correo
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_USER = "maruansaidi22@gmail.com"
EMAIL_PASS = "originalmarouanesr9200202020*"
RECIPIENT_EMAIL = "infmarouane@gmail.com"

# Ruta de los archivos CSV
CSV_FOLDER = "C:\"

# Función para procesar LogText
def process_log_text(log_text):
    # Extraer el número de ocurrencias
    occurrences = int(re.search(r"(\d+) occurrence\(s\)", log_text).group(1))

    # Extraer el archivo afectado
    file_path = re.search(r"on file \[(.*?)\]", log_text).group(1)

    # Determinar el tipo de archivo (Datos o Log)
    if "_Data" in file_path or file_path.endswith(('.ndf', '.mdf', '.')):
        file_type = "Datos"
    elif "_Log" in file_path or file_path.endswith('.ldf'):
        file_type = "Log"
    else:
        file_type = "Desconocido"

    # Extraer la base de datos (asumimos que está en el nombre del archivo)
    db_name_match = re.search(r"\\(\w+)_", file_path)
    db_name = db_name_match.group(1) if db_name_match else "Desconocida"

    return occurrences, db_name, file_type

# Función para cargar los dos archivos CSV más recientes
def load_recent_csvs():
    csv_files = sorted(
        glob.glob(f"{CSV_FOLDER}/*.csv"), key=lambda x: Path(x).stat().st_mtime, reverse=True
    )
    if len(csv_files) < 2:
        raise ValueError("No hay suficientes archivos CSV en la carpeta para comparar.")
    return csv_files[0], csv_files[1]  # Archivo más reciente y anterior

# Procesar los CSV para generar el análisis
def analyze_data(recent_csv, previous_csv):
    # Cargar archivos CSV
    recent_df = pd.read_csv(recent_csv)
    previous_df = pd.read_csv(previous_csv)

    # Procesar la columna LogText para el archivo reciente
    recent_processed = recent_df['LogText'].apply(lambda x: process_log_text(x))
    recent_df[['Ocurrencias', 'Base de Datos', 'Tipo']] = pd.DataFrame(
        recent_processed.tolist(), index=recent_df.index
    )

    # Agrupar y resumir los datos del reciente
    recent_summary = recent_df.groupby(['Base de Datos', 'Tipo']).agg(
        Total_Ocurrencias=('Ocurrencias', 'sum')
    ).reset_index()

    # Procesar la columna LogText para el archivo anterior
    previous_processed = previous_df['LogText'].apply(lambda x: process_log_text(x))
    previous_df[['Ocurrencias', 'Base de Datos', 'Tipo']] = pd.DataFrame(
        previous_processed.tolist(), index=previous_df.index
    )

    # Agrupar y resumir los datos del anterior
    previous_summary = previous_df.groupby(['Base de Datos', 'Tipo']).agg(
        Total_Ocurrencias=('Ocurrencias', 'sum')
    ).reset_index()

    # Calcular la diferencia total de ocurrencias
    total_recent = recent_df['Ocurrencias'].sum()
    total_previous = previous_df['Ocurrencias'].sum()
    total_difference = total_recent - total_previous

    # Generar el texto del informe
    report = f"Durante la semana se han producido un total de {total_recent} incidencias de picos de latencia E/S. "
    report += f"Esto supone un total de {abs(total_difference)} {'más' if total_difference > 0 else 'menos'} que la semana anterior.\n\n"

    for _, row in recent_summary.iterrows():
        db_name = row['Base de Datos']
        file_type = row['Tipo']
        total = row['Total_Ocurrencias']
        report += f"La base de datos “{db_name}” tuvo un total de {total} incidencias "
        if file_type == "Datos":
            report += "en ficheros de datos. "
        elif file_type == "Log":
            report += "en ficheros de log transaccionales. "
        report += "\n"

    return report, recent_csv

# Enviar correo electrónico con el informe y el CSV adjunto
def send_email(report, attachment):
    # Crear mensaje de correo
    msg = MIMEMultipart()
    msg['From'] = 'maruansadi22@gmail.com'
    msg['To'] = 'infmarouane@gmail.com'
    msg['Subject'] = "Informe semanal de picos de latencia E/S"

    # Adjuntar el cuerpo del mensaje
    msg.attach(MIMEText(report, 'plain'))

    # Adjuntar archivo CSV
    with open(attachment, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={Path(attachment).name}')
    msg.attach(part)

    # Conectar al servidor SMTP y enviar el correo
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

# Función principal
def main():
    try:
        recent_csv, previous_csv = load_recent_csvs()
        report, attachment = analyze_data(recent_csv, previous_csv)
        send_email(report, attachment)
        print("Correo enviado correctamente.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
