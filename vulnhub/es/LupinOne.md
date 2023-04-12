[Read on English](https://github.com/14wual/pwned/vulnhub/en/LupinOne.md)

# LupinOne

Plataform: [Vulnhub](https://www.vulnhub.com/)

Serie: [Series Empire](https://www.vulnhub.com/series/empire,507/)

Máquina: [LupinOne](https://www.vulnhub.com/entry/empire-lupinone,750/)

Nivel: Medio

See more: [link](<paste here the link>)

## Walkthrough - Video

Ver Vídeo: [LupinOne | Vulnhub - Series Empire | Walkthrough |WualPk](<paste here the link>)
Canal de YouTube: [YouTube | @wual](htttp://www.youtube.com/@wual)
Lista de Reproducción: [Machines Pwned](<paste here the link>)

## Walkthrough


´´´bash
# sudo nmap -sV <puerta de enlace>/24
$ sudo nmap -sV 192.168.1.1/24
´´´


Mi **Output** Personal: ´192.168.1.110´ | Este es la IP Privada de mi máquina.

Cuando conseguimos la ip victima (`target`), vamos ha realizar un escaneo sobre la máquina. La realizaremos con las siguientes **flags**: ´-sC´ (para obtener la máxima info posible a partir de unos scripts de nmap por defecto) y ´-sV´ (para darme todos los servicios que corren en los puertos abiertos.)


´´´bash
# sudo nmap -sV <ip-víctima>/24
$ sudo nmap -sC -sV 192.168.1.110
´´´


*Output*:


```ini
[Puertos Abiertos]
ssh = 22/tcp # Nos sugiere que se puede entrar a partir de una cuenta
http = 80/tcp # Entre ellas encontramos un directorio (myfiles)
```


De esta manera, ya sabemos que existe una **página web**. Asi que, nos vamos al navagador y la **barra de dirreciones** escribimos `http://<ip-victima>`


```
# http://<ip-victima>/
$ http://192.168.1.110/
```


En esta página web, encontramos una imagen, y si leemos un poco el códgio fuente de esta, encontraremos un `<!-- Comentario -->`, pero este no es de mucha utilidad. Además, vamos ha intentar entrar en el directorio que antes vimo al realizar el escaneo: `http://<ip-victima>/myfiles`. Encontramos una Página de **Error 404** y en su código fuente encontramos otro comentario sin utilidad.

Llegados a este punto, vamos ha realizar un **Ataque de Fuerza Bruta de Directorios** con una herramienta llamada **ffuf**. Esto lo realizaremos con un diccionario que podremos encontrar el repositorio github de [danielmiessler/SecLists](https://github.com/danielmiessler/SecLists). Para usarlo, clonaremos el repositorio en la carpeta de nuestra conveniencia (en mi caso ``$user/Documents`) de la manera que el propio *Readme* nos muestra:


```
wget -c https://github.com/danielmiessler/SecLists/archive/master.zip -O SecList.zip \
  && unzip SecList.zip \
  && rm -f SecList.zip
```


Para encontrar el diccionario exacto que buscamos (common.txt) realizaremos un find. De esta manera obtendremos el **Path**.


```
find . -name common.txt
```


Después de tener la dirección, realizamos el siguiente comando: (la flag -c es para adelantar la ejecución)


´´´bash
# sudo ffuf -c -w <URL-DICCIONARIO> -u <IP-VÍCTIMA>/~FUUZ
$ sudo ffuf -c -w <URL-DICCIONARIO> -u 192.168.1.110/~FUUZ
´´´


Al realizar este comando, obtenemos un nuevo directorio: ´/~secret/´ , en el encontramos un mensaje de un usuario llamado `icex64`, donde nos diece que hay un hash escondido en la máquina, además, nos muestra un posible usuario.

Vamos ha volver a realizar el ataque de fuerza bruta pero esta vez a directorios escondidos en ´/~secret/´:


´´´bash
# sudo ffuf -c -ic -w <URL-DICCIONARIO> -u <IP-VÍCTIMA>/~FUUZ -fc 403 -e .txt, .html
$ sudo ffuf -c -ic -w <URL-DICCIONARIO> -u 192.168.1.110/~FUUZ -fc 403 -e .txt, .html
´´´
