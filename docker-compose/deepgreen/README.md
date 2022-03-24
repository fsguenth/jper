

How to run deepgreen jper docker in first time
--------------------------------------------------------
```shell
cd jper/docker-compose/deepgreen/
docker-compose up --build

# on *other* terminal run following command to make sure service is runnning
curl http://localhost:5998/account/login
curl http://localhost:9200

# after all service ready, run following command to load develop data to DB
docker exec -it deepgreen_jper-web_1 python3 /opt/jper/service/scripts/autoload_dev_data.py
```

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
