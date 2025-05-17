import os
from django.shortcuts import render
import geoip2.database

# GeoLite2 fájl elérési útja (állítsd be helyesen a projektedben)
DB_PATH = os.path.join(os.path.dirname(__file__), 'GeoLite2-City.mmdb')

def geoip(request):
    results = []
    error = None

    if request.method == "POST":
        ip_list = []

        uploaded_file = request.FILES.get('ip_file')

        if uploaded_file:
            try:
                content = uploaded_file.read().decode('utf-8')
                ip_list = [ip.strip() for ip in content.replace(',', '\n').splitlines() if ip.strip()]
            except Exception as e:
                error = f"Fájl olvasási hiba: {str(e)}"
        else:
            ip_input = request.POST.get('ip_addresses', '')
            ip_list = [ip.strip() for ip in ip_input.replace(',', '\n').splitlines() if ip.strip()]

        if not error:
            try:
                reader = geoip2.database.Reader(DB_PATH)
            except Exception as e:
                error = f"Adatbázis megnyitási hiba: {str(e)}"
                reader = None

            if reader:
                for ip in ip_list:
                    try:
                        response = reader.city(ip)
                        results.append({
                            'ip': ip,
                            'country': response.country.name,
                            'region': response.subdivisions.most_specific.name,
                            'city': response.city.name,
                        })
                    except geoip2.errors.AddressNotFoundError:
                        results.append({'ip': ip, 'error': 'IP nem található'})
                    except Exception as e:
                        results.append({'ip': ip, 'error': str(e)})
                reader.close()

    else:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        try:
            reader = geoip2.database.Reader(DB_PATH)
            response = reader.city(ip)
            results.append({
                'ip': ip,
                'country': response.country.name,
                'region': response.subdivisions.most_specific.name,
                'city': response.city.name,
            })
            reader.close()
        except Exception as e:
            error = f'Nem sikerült lekérni az IP adatokat: {str(e)}'

    return render(request, 'geoip/geoip.html', {
        'results': results,
        'error': error
    })
