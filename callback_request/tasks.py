from celery.task import task


@task(name='callback_request.delayed_request')
def delayed_request(request_id):
    from callback_request.models import CallbackRequest

    callback_request = CallbackRequest.objects.get(pk=request_id)
    if callback_request.completed or callback_request.error:
        return
    callback_request.make_call()
