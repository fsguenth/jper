# Code to create new index with changed mapping

# Delete all of the data in lic rel file and do script again to match participant

# Make index read only
curl -X PUT \
  http://localhost:9205/jper-unrouted/_settings \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'postman-token: 9bc70404-1581-b572-de7e-77b0463980fd' \
  -d '{
  "settings": {
    "index.blocks.write": true
  }
}'


# Clone the index
curl -X POST \
  http://localhost:9205/jper-unrouted/_clone/jper-unrouted-cloned \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'postman-token: 7e051434-9942-ff3f-ff3d-4ab18b90fcc7'
  

  
# Remove read only
curl -X PUT \
  http://localhost:9205/jper-license/_settings \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'postman-token: a7ca473c-b986-7f7e-e943-1a411295774b' \
  -d '{
  "settings": {
    "index.blocks.write": false
  }
}'


# create index with new mapping
curl -X PUT \
  http://localhost:9205/jper-unrouted-cloned/ \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'postman-token: 8ff319c9-8a0c-c4aa-a8f6-f0ce00eb8642' \
  -d '{

    "mappings": {
        "dynamic_templates": [
            {
                "strings": {
                    "match_mapping_type": "string",
                    "mapping": {
                        "fields": {
                            "exact": {
                                "normalizer": "lowercase",
                                "type": "keyword"
                            }
                        },
                        "type": "text"
                    }
                }
            }
        ],
        "properties": {
            "content": {
                "properties": {
                    "packaging_format": {
                        "type": "text",
                        "fields": {
                            "exact": {
                                "type": "keyword",
                                "normalizer": "lowercase"
                            }
                        }
                    }
                }
            },
            "created_date": {
                "type": "date"
            },
            "embargo": {
                "properties": {
                    "duration": {
		                "type": "text",
		                "fields": {
		                    "exact": {
		                        "type": "keyword",
		                        "normalizer": "lowercase"
		                    }
		                }
                    }
                }
            },
            "id": {
                "type": "text",
                "fields": {
                    "exact": {
                        "type": "keyword",
                        "normalizer": "lowercase"
                    }
                }
            },
            "last_updated": {
                "type": "date"
            },
            "links": {
                "properties": {
                    "access": {
                        "type": "text",
                        "fields": {
                            "exact": {
                                "type": "keyword",
                                "normalizer": "lowercase"
                            }
                        }
                    },
                    "format": {
                        "type": "text",
                        "fields": {
                            "exact": {
                                "type": "keyword",
                                "normalizer": "lowercase"
                            }
                        }
                    },
                    "packaging": {
                        "type": "text",
                        "fields": {
                            "exact": {
                                "type": "keyword",
                                "normalizer": "lowercase"
                            }
                        }
                    },
                    "type": {
                        "type": "text",
                        "fields": {
                            "exact": {
                                "type": "keyword",
                                "normalizer": "lowercase"
                            }
                        }
                    },
                    "url": {
                        "type": "text",
                        "fields": {
                            "exact": {
                                "type": "keyword",
                                "normalizer": "lowercase"
                            }
                        }
                    }
                }
            },
            "location": {
                "type": "geo_point"
            },
            "metadata": {
                "properties": {
                    "license_ref": {
                        "properties": {
                            "title": {
                                "type": "text",
                                "fields": {
                                    "exact": {
                                        "type": "keyword",
                                        "normalizer": "lowercase"
                                    }
                                }
                            },
                            "type": {
                                "type": "text",
                                "fields": {
                                    "exact": {
                                        "type": "keyword",
                                        "normalizer": "lowercase"
                                    }
                                }
                            },
                            "url": {
                                "type": "text",
                                "fields": {
                                    "exact": {
                                        "type": "keyword",
                                        "normalizer": "lowercase"
                                    }
                                }
                            },
                            "version": {
                                "type": "text",
                                "fields": {
                                    "exact": {
                                        "type": "keyword",
                                        "normalizer": "lowercase"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "provider": {
                "properties": {
                    "id": {
                        "type": "text",
                        "fields": {
                            "exact": {
                                "type": "keyword",
                                "normalizer": "lowercase"
                            }
                        }
                    }
                }
            }
        }
    }

}'


INDEX_NAME=jper-license
NEW_INDEX_NAME=${INDEX_NAME}-cloned

echo ""
echo "Re-index from old to new"
echo ""
curl -X POST \
  http://localhost:9205/_reindex \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{
  "source": {
    "index": "'${NEW_INDEX_NAME}'"
  },
  "dest": {
    "index": "'${INDEX_NAME}'"
  }
}'


# Delete all docs from index

curl -X POST \
  http://localhost:9205/jper-unrouted/_delete_by_query \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'postman-token: 7695a50a-59ad-9fc7-d326-9e9e2789cc8f' \
  -d '{
  "query": {
    "match_all": {}
  }
}'


# Close an index

curl -X POST \
  http://localhost:9205/jper-sword_%2A/_close \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'postman-token: 52205595-7d06-efdd-7cbc-047c2517a933'
  
  
# Delete an index
curl -X DELETE \
  http://localhost:9205/jper-license-cloned \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'postman-token: 0f8cc732-ed03-1163-4541-659f56eed618'
  
  

