# amazon_scrapper_with_fastapi_nosql
Scrape websites with Python, Selenium, Requests HTML, Celery, FastAPI, &amp; NoSQL with Cassandra via AstraDB.


1. Git clone
2. install all requirements: pip install -r requirements.txt
3. run FastAPI: uvicorn app.main:app --reload
4. run celery docker: sudo docker run -it --rm redis
5. run celery app: celery --app app.worker.celery_app worker --beat -s celerybeat-schedule --loglevel INFO

