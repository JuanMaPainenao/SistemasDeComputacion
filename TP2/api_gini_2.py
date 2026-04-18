import requests

params = {
    'format': 'json',
    'date': '2011:2020',
    'per_page': 32500,
    'page': 1
}

url = 'https://api.worldbank.org/v2/en/country/all/indicator/SI.POV.GINI'

def obtener_gini_argentina():
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status() 
        lista_datos = res.json()[1]

        for registro in lista_datos:
            if registro['country']['id'] == 'AR' and registro['value'] is not None:
                return float(registro['value'])
        return None

    except requests.exceptions.Timeout:
        print("Timeout")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error de red: {e}")
        return None

valor = obtener_gini_argentina()
print(f"Índice GINI Argentina: {valor}")
#print(res)
#print(res.text)