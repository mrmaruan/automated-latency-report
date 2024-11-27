# automated-latency-report
Automatización del reporte semanal de incidencias por picos de latencia E/S.

# Automated Latency Report

Este proyecto tiene como objetivo automatizar el proceso de envío de reportes semanales de incidencias por picos de latencia en las bases de datos. El sistema compara el número de incidencias de la semana actual con las de la semana anterior y genera un correo electrónico informando al cliente sobre las diferencias.

## Características

- Compara los datos de incidencias entre dos semanas.
- Genera un correo electrónico con el informe y las incidencias clasificadas en log y datos.
- Adjunta automáticamente el archivo CSV con las incidencias.
- Envío del correo a través de SMTP (configurado para Gmail por defecto).
- Automáticamente encuentra el archivo CSV más reciente si el nombre cambia cada semana.

## Requisitos

- Python 3.x
- Pandas (para la manipulación de archivos CSV)
- smtplib (para el envío de correos)
- Otras dependencias (ver `requirements.txt`)

## Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/mrmaruan/automated-latency-report.git
