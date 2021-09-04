# Teeskins discord bot

#### How to install dependencies ?

```bash
bash install.sh
```

#### env

Copy `json/env_example.json` to `json/env.json` and replace values 

#### Docker

```bash
docker build -t teeskins .
docker run -it -v $PWD/public:/app/public teeskins
```
