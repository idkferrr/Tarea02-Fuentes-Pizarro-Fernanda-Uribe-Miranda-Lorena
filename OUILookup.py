#Fernanda Fuentes Pizarro, fernanda.fuentesp@alumnos.uv.cl
#Lorena Uribe Miranda, lorena.uribe@alumnos.uv.cl

import sys
import getopt
import requests
import subprocess
import re

def usage():
    
    # Muestra cómo utilizar el programa y qué opciones de línea de comandos están disponibles.
    
    print("Use: python OUILookup.py --mac <mac> | --arp | [--help]")
    print("--mac: MAC a consultar. P.e. aa:bb:cc:00:00:00")
    print("--arp: muestra los fabricantes de los hosts disponibles en la tabla ARP")
    print("--help: muestra este mensaje y termina.")

def lookup_mac(mac):
    try:
        # Se construye la URL para consultar la MAC
        url = f"https://api.maclookup.app/v2/macs/{mac}"
        # Se hace la solicitud GET a la API
        response = requests.get(url)
        # La respuesta se convierte en formato JSON
        data = response.json()

        # Si se encuentra el campo 'company' con valor, se muestra el fabricante
        if 'company' in data and data['company']:
            print(f"MAC address : {mac}")
            print(f"Fabricante  : {data['company']}")
        else:
            # Si no se encuentra el fabricante
            print(f"MAC address : {mac}")
            print("Fabricante  : No se encontró en la base de datos")
    except Exception as e:
        # Si ocurre un error durante la solicitud, se muestra un mensaje de error
        print(f"Error al consultar la MAC: {e}")

def is_special_mac(mac):
   
    # Las MACs que empiezan con 'ff-ff-ff' (broadcast) o '01-00-5e' (multicast) son filtradas
    return mac.startswith('ff-ff-ff') or mac.startswith('01-00-5e')

def lookup_arp():
   
    try:
        # Ejecutamos el comando 'arp -a' para obtener la tabla ARP
        result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE, text=True)
        # Guardamos la salida del comando (la tabla ARP)
        arp_output = result.stdout
        print("Tabla ARP:")
        print(arp_output)
        
        # Usamos una expresión regular para encontrar todas las MACs en la tabla ARP
        macs = re.findall(r'([0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2})', arp_output)
        # Removemos duplicados para no consultar la misma MAC más de una vez
        unique_macs = set(macs)
        
        # Para cada MAC en la tabla ARP
        for mac in unique_macs:
            # Si la MAC no es especial (como broadcast o multicast), la consultamos en la API
            if not is_special_mac(mac):
                print(f"\nConsultando fabricante para la MAC: {mac}")
                lookup_mac(mac)

    except Exception as e:
        # Si ocurre algún error al obtener la tabla ARP, lo mostramos
        print(f"Error al obtener la tabla ARP: {e}")

def test_macs():
  
    test_mac_addresses = ['98:06:3c:92:ff:c5', '9c:a5:13', '48-E7-DA']
    
    # Para cada MAC de prueba, llamamos a 'lookup_mac' para obtener el fabricante
    for mac in test_mac_addresses:
        print(f"\nProbando la MAC: {mac}")
        lookup_mac(mac)

def main():
    try:
        # Procesamos los argumentos de entrada (como --mac, --arp, --help, --test)
        opts, args = getopt.getopt(sys.argv[1:], "", ["mac=", "arp", "help", "test"])
    except getopt.GetoptError as err:
        # Si hay un error en los argumentos, mostramos el uso correcto y salimos
        print(err)
        usage()
        sys.exit(2)
    mac = None
    arp = False
    test = False
    # Revisamos cada opción ingresada en la línea de comandos
    for o, a in opts:
        if o == "--mac":
            mac = a  # Guardamos la MAC a consultar
        elif o == "--arp":
            arp = True  # Indicamos que se debe consultar la tabla ARP
        elif o == "--test":
            test = True  # Activamos el modo de prueba
        elif o == "--help":
            usage()
            sys.exit()
    # Si se ingresó una MAC, la consultamos
    if mac:
        lookup_mac(mac)
    # Si se pidió la tabla ARP, la obtenemos y consultamos las MACs
    elif arp:
        lookup_arp()
    # Si se activó el modo de prueba, ejecutamos las pruebas
    elif test:
        test_macs()
    else:
        # Si no se ingresó ninguna opción válida, mostramos cómo usar el programa
        usage()

if __name__ == "__main__":
    main()
