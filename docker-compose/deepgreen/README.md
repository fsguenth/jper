

Useful command
-------------------------
### run all services
```shell
docker-compose up
```

### run all services and force rebuild
```shell
docker-compose up --build
```

### remove all volume 
```shell
docker rm -f deepgreen_elasticsearch_1 deepgreen_store_1 deepgreen_jper-web_1 deepgreen_jper-pychrame_1 && docker-compose down -v
```
