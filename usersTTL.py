import asyncio
from datetime import datetime, timedelta
from copy import deepcopy

class TTLDict:
    def __init__(self, ttl_seconds):
        self.ttl_seconds = ttl_seconds
        self.data = {}
        self.locks = {}
        self.tasks = {}
        self.global_lock = asyncio.Lock()
        #asyncio.create_task(self.print_users_periodically())

    async def _remove_user(self, user_id):
        await asyncio.sleep(self.ttl_seconds)
        async with self.global_lock:
            user_lock = self.locks.get(user_id)
            if user_lock:
                async with user_lock:
                    if user_id in self.data:
                        user_data = self.data[user_id]
                        if datetime.now() - user_data['timestamp'] >= timedelta(seconds=self.ttl_seconds):
                            del self.data[user_id]
                            del self.locks[user_id]
                            print(f"Usuario {user_id} eliminado por inactividad")
                        else:
                            print(f"Usuario {user_id} no eliminado, tiempo de inactividad insuficiente")
                            self._schedule_remove(user_id)

    def _schedule_remove(self, user_id):
        if user_id in self.tasks:
            self.tasks[user_id].cancel()
        self.tasks[user_id] = asyncio.create_task(self._remove_user(user_id))

    async def add_or_update_user(self, user, updates={}):
        async with self.global_lock:
            if user not in self.locks:
                self.locks[user] = asyncio.Lock()

        async with self.locks[user]:
            if user not in self.data:
                self.data[user] = {'timestamp': datetime.now()}
            self.data[user]['timestamp'] = datetime.now()
            self.data[user].update(updates)

        self._schedule_remove(user)
        print(f"Usuario {user} actualizado.")

    async def get_user(self, user):
        async with self.global_lock:
            user_lock = self.locks.get(user)
            if user_lock:
                async with user_lock:
                    user_data = self.data.get(user)
                    if user_data and datetime.now() - user_data['timestamp'] < timedelta(seconds=self.ttl_seconds):
                        user_data['timestamp'] = datetime.now()
                        self._schedule_remove(user)
                        return {k: v for k, v in user_data.items() if k != 'timestamp'}
                    else:
                        return None
            else:
                return None

    async def get_user_key(self, user, key):
        async with self.global_lock:
            user_lock = self.locks.get(user)
            if user_lock:
                async with user_lock:
                    user_data = self.data.get(user)
                    if user_data and datetime.now() - user_data['timestamp'] < timedelta(seconds=self.ttl_seconds):
                        user_data['timestamp'] = datetime.now()
                        self._schedule_remove(user)
                        return user_data.get(key, None)
                    else:
                        return None
            else:
                return None

    async def append_to_user_list(self, user, key, value):
        async with self.global_lock:
            user_lock = self.locks.get(user)
            if user_lock:
                async with user_lock:
                    user_data = self.data.get(user)
                    if user_data and datetime.now() - user_data['timestamp'] < timedelta(seconds=self.ttl_seconds):
                        if key in user_data:
                            if isinstance(user_data[key], list):
                                user_data[key].append(value)
                                user_data['timestamp'] = datetime.now()
                                self._schedule_remove(user)
                                return True
                            else:
                                raise ValueError(f"El valor para la clave '{key}' no es una lista")
                        else:
                            raise KeyError(f"La clave '{key}' no existe para el usuario '{user}'")
                    else:
                        return False
            else:
                return False

    async def update_lista_de_mensajes(self, user, key, new_message):
        async with self.global_lock:
            user_lock = self.locks.get(user)
            if user_lock:
                async with user_lock:
                    user_data = self.data.get(user)
                    if user_data and datetime.now() - user_data['timestamp'] < timedelta(seconds=self.ttl_seconds):
                        lista = user_data.get(key, None)
                        if lista is not None and isinstance(lista, list):
                            lista[0] = new_message
                            user_data['timestamp'] = datetime.now()
                            self._schedule_remove(user)
                            return True
                        else:
                            raise KeyError(f"La clave '{key}' no existe o no es una lista para el usuario '{user}'")
                    else:
                        return False
            else:
                return False

    async def delete_user_key(self, user_id, key):
        async with self.global_lock:
            user_lock = self.locks.get(user_id)
            if user_lock:
                async with user_lock:
                    user_data = self.data.get(user_id)
                    if user_data and datetime.now() - user_data['timestamp'] < timedelta(seconds=self.ttl_seconds):
                        if key in user_data:
                            del user_data[key]
                            user_data['timestamp'] = datetime.now()
                            self._schedule_remove(user_id)
                            return True
                        else:
                            return False  # Key no encontrada
                    else:
                        return False  # Usuario inactivo o no encontrado
            else:
                return False  # Lock no encontrado

    async def get_user_key_DEEP_COPY(self, user, key):
        async with self.global_lock:
            user_lock = self.locks.get(user)
            if user_lock:
                async with user_lock:
                    user_data = self.data.get(user)
                    if user_data and datetime.now() - user_data['timestamp'] < timedelta(seconds=self.ttl_seconds):
                        user_data['timestamp'] = datetime.now()
                        self._schedule_remove(user)
                        return deepcopy(user_data.get(key, None))
                    else:
                        return None
            else:
                return None

    async def print_users_periodically(self):
        while True:
            async with self.global_lock:
                print("Estado actual de los usuarios:", self.data)
            await asyncio.sleep(10)

    def __repr__(self):
        return repr(self.data)

ttl_users = TTLDict(3600)

