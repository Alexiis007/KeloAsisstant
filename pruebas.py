import requests
import json

# URL del servidor de Ollama y el nombre del modelo
modelo = "mistral"  # Cambia esto por el nombre de tu modelo
url = "http://127.0.0.1:11434/api/chat"  # Cambia esto si es necesario
data = {
    "model": "mistral:latest",  # Nombre correcto del modelo
    "messages": [{"role": "user", "content": "Hola, ¿cómo estás?"}]
}

response = requests.post(url, json=data)

# Comprobar la respuesta
if response.status_code == 200:
    # Dividir la respuesta en líneas
    response_lines = response.text.strip().splitlines()
    contents = []

    # Procesar cada línea
    for line in response_lines:
        try:
            json_line = json.loads(line)
            if 'message' in json_line:
                contents.append(json_line['message']['content'])
        except json.JSONDecodeError as e:
            print(f"Error al decodificar la línea: {line}\nError: {e}")

    # Unir todos los contenidos en un solo string
    full_response = ''.join(contents)
    print(full_response)
else:
    print(f"Error: {response.status_code}")


