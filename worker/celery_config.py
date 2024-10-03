from celery import Celery

app = Celery('worker', broker='amqp://my_personal_user:my_personal_password@rabbitmq:5672//')

app.conf.update(
    result_backend='rpc://',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    include=['worker.tasks']
)

if __name__ == '__main__':
    app.start()