from items import Weapon, Rarity
from engine.rl import QLearningAgent
from system.game_logging import get_episode_logger


import random

class Monster():
    list_monster = []
    def __init__(self, weapon : Weapon, pv=100, x=0.0, y=0.0, dx=1, dy=0, speed=0.33):
        self.pv=pv
        self.weapon=weapon
        self.x=int(x)
        self.y=int(y)
        self.dx=int(dx)
        self.dy=int(dy)
        self.speed = float(speed)
        self._move_acc = 0.0 

        self.rl_agent = None
        self.rl_steps = 0

        Monster.list_monster.append(self)
    
    ###### getters and setters ######

    def get_is_alive(self):
        return self.pv>0
    
    def get_pv(self):
        return self.pv
    
    def heal(self,soin):
        self.pv+=soin

    def get_equiped_item(self):
        # ancien: return self.equiped_item
        return self.weapon
    
    def get_equiped_item(self):
        return self.weapon

    def get_damage(self):
        """
        return damage of equipied weapon or default damage (5).
        """
        if self.weapon:
            return self.weapon.damage
        return 5

    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

    def get_position(self):
        return (self.x, self.y)

    def set_pv(self, pv):
        self.pv = pv

    def set_equiped_item(self, equiped_item):
        self.weapon = equiped_item
    
    def set_x(self, x):
        self.x = int(x)
    
    def set_y(self, y):
        self.y = int(y)
    
    def set_position(self, x, y):
        self.x = int(x)
        self.y = int(y)

    
    def set_speed(self, speed: float):
        self.speed = max(0.0, float(speed))


    ###### RL methods ######

    def _ensure_rl(self):
        if self.rl_agent is None:
            self.rl_agent = QLearningAgent(epsilon=0.2)

    def _state(self, player_pos, clip=6):
        px, py = player_pos
        dx = max(-clip, min(clip, px - self.x))
        dy = max(-clip, min(clip, py - self.y))
        return (dx, dy)

    @staticmethod
    def _offset_from_action(a):
        if a == 0:   return (0, -1)  # up
        if a == 1:   return (0,  1)  # down
        if a == 2:   return (-1, 0)  # left
        if a == 3:   return (1,  0)  # right
        raise ValueError("action inconnue")

    def _try_action_on_map(self, game_map, action, player_pos):
        """
        Tente un déplacement.
        Return (next_state, reward, done, applied_bool).
        Reward: -1/step, -5 si mur, +20 si joueur autour de lui.
        """
        ax, ay = self._offset_from_action(action)
        nx, ny = self.x + ax, self.y + ay

        reward = -1.0
        applied = False

        # Collision (bornes + walkable)
        if 0 <= nx < game_map.width and 0 <= ny < game_map.height and game_map.is_walkable(nx, ny):
            # éviter chevauchement autre monstre
            occupied = any((m is not self) and (getattr(m, "x", None) == nx and getattr(m, "y", None) == ny)
                           for m in game_map.enemies)
            if occupied:
                reward += -2.0
                nx, ny = self.x, self.y
            else:
                applied = True
        else:
            reward += -5.0
            nx, ny = self.x, self.y
        
        # distance avant/après (même si le move est annulé)
        px, py = player_pos
        # distance de Manhattan (plus stable pour grille)
        d_old = abs(px - self.x) + abs(py - self.y)
        d_new = abs(px - nx) + abs(py - ny)

        # Reward dense : bonus si on se rapproche, malus si on s'éloigne
        reward += 0.6 * (d_old - d_new)

        if applied:
            self.x, self.y = nx, ny

        px, py = player_pos
        done = (self.x == px and self.y == py)
        if done:
            reward += 20.0

        return self._state(player_pos), reward, done, applied

    def rl_step(self, game_map, player_pos):
        """
        Un pas d'APPR pour ce monstre : choisir action, bouger, update Q.
        Retourne True si le joueur est atteint.
        """
        self._ensure_rl()
        s = self._state(player_pos)
        a = self.rl_agent.select(s)
        s2, r, done, _ = self._try_action_on_map(game_map, a, player_pos)
        self.rl_agent.update(s, a, r, s2, done)
        location_type = game_map.get_location_type(self.x, self.y)
        # log transition RL
        ep = get_episode_logger()
        ep.log_transition(
            monster_id=id(self),
            s=list(s),
            a=int(a),
            r=float(r),
            s2=list(s2),
            done=bool(done),
            tick=game_map.ticks,
            pos=[self.x, self.y],
            location=location_type, # AJOUT: Passer le contexte

        )
        self.rl_steps += 1
        if self.rl_steps % 10 == 0:
            self.rl_agent.decay()
        return done
    
    ###### other methods ######

    def die(self, drop_rate=0.5):
        """
        Handle the monster's death and item drop.
        drop_rate: Probability of dropping the equipped weapon (0.0 to 1.0).
        """
        if not self.get_is_alive():
            if self.weapon and (random.random() < drop_rate):
                print(f"Dropped item: {self.weapon.name}")
                return self.weapon
            print("Monster has died.")
        else :
            print("Monster's pv are still above 0.")
            return None
    
    def kill(self, drop_rate=1.0):
        """
        Instantly kill the monster by setting its health to 0.
        """
        self.pv = 0
        dropped_item=self.die(drop_rate)
        return dropped_item

    def kill_all_monsters(self):
        """
        Instantly kill all monsters in the list.
        """
        for monster in Monster.list_monster:
            monster.kill()


if __name__ == "__main__":
    # Example usage
    sword = Weapon(name="Sword",description="a sharp blade",rarity=Rarity.LEGENDARY, damage=15, category="melee", range=1.5, durability=10)
    goblin = Monster(weapon=sword, pv=50, x=5.0, y=10.0)
    
    print(f"Goblin's initial health: {goblin.get_pv()}")
    dropped_item=goblin.kill()  # Simulate the goblin taking damage
    if dropped_item:
        print(f"Goblin dropped: {dropped_item.name}")
    else:
        print("Goblin did not drop any item.")
    
