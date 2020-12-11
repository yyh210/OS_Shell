import time
from threading import Thread


class PCB(object):
    def __init__(self, pid, st, sl, priority, pName=None, parent=None, son=None):
        self.pid = pid
        self.st = st
        self.sl = sl
        self.priority = priority
        self.parent = parent
        self.son = son
        self.brother = None
        self.pName = pName
        self.pNext = None  # next ready p in the same priority
        self.pPre = None  # previous ready p in the same priority
        self.occupied = []
        self.blocked_res = {}  # save rid

    def __str__(self):
        return self.pName

    def block(self, rid, num):
        if type(self.sl) != list:
            self.sl = []
        if rid not in self.sl:
            self.sl.append(rid)
            self.blocked_res[rid] = num

    def insert(self, rid):  # save id for the occupied resources and update blocked list
        if rid not in self.occupied:
            self.occupied.append(rid)

    def delete(self):
        flag = 0
        head = self.sl
        if self.st != 'blocked':
            if self.pPre is not None:  # not first
                self.pPre.pNext = self.pNext
                if self.pNext is not None:
                    self.pNext.pPre = self.pPre
            else:  # first
                head[self.priority] = self.pNext
                if self.pNext is not None:  # tail
                    self.pNext.pPre = None

            flag = 1
        else:  # head == blocked list
            for i in range(len(head)):
                if head[i].pid == self.pid:
                    del head[i]
                    flag = 1
                    break
        if not flag:
            print("Process was not found")


class RCB(object):
    def __init__(self, rid, N):
        self.rid = rid
        self.N = N
        self.remain = N
        self.rName = 'R' + str(rid)
        self.occupy_list = {}
        self.blocked = []  # keep FIFO

    def __str__(self):
        return "rid: " + str(self.rid) + ',' + "remain: " + str(self.remain)

    def insert(self, pid, num):
        if pid not in self.occupy_list.keys():
            self.occupy_list[pid] = num
        else:
            self.occupy_list[pid] += num
        for i in range(len(self.blocked)):  # if p was blocked then remove if from blocked list
            if self.blocked[i] == pid:
                del self.blocked[i]
        self.remain -= num

    def block(self, pid):
        self.blocked.append(pid)

    def release(self, pcb: PCB, num=None):
        pid = pcb.pid
        if num is None:
            num = self.occupy_list[pid]
        if self.occupy_list[pid] == num:
            del self.occupy_list[pid]  # 解除rcb占用
            for i in range(len(pcb.occupied)):
                if pcb.occupied[i] == self.rid:  # 解除pcb占用
                    del pcb.occupied[i]
                    break
            if pcb.st == 'blocked':
                for i in range(len(self.blocked)):  # 更新blocked
                    if self.blocked[i] == pid:
                        del self.blocked[i]
                # update pcb: blocked_res, sl
                for i in range(len(pcb.sl)):
                    if pcb.sl[i] == self.rid:
                        del pcb.sl[i]
                        del pcb.blocked_res[self.rid]
        else:
            self.occupy_list[pid] -= num

        self.remain += num


class YShell():
    def __init__(self):
        Thread.__init__(self)
        self.cmd_set = {'cr': self.cr,
                        'de': self.de,
                        'req': self.req,
                        'rel': self.rel,
                        'to': self.to,
                        'list': self.list,
                        'exit': self.exit,
                        'read': None,
                        'ls': self.list}
        self.RL = {2: None, 1: None, 0: None}
        self.BL = []
        self.resources = [RCB(1, 1), RCB(2, 2), RCB(3, 3), RCB(4, 4)]
        self.pCnt = 0
        init = PCB(self.pCnt, 'running', self.RL, 0, 'init', None)
        self.pCnt += 1
        init.sl[init.priority] = init
        self.flag = True
        '''
            资源初始化， 启动init进程
        '''

    def run(self):
        flag = True
        while (flag):
            r_user_in = input('yyh@shell>')

            user_in = r_user_in.strip().split()  # 默认空白符分割， 有点牛逼哦
            cmd = user_in.pop(0)
            parameters = user_in
            if cmd == 'read':
                f = open("in.txt", 'r+')
                for line in f.readlines():
                    user_in = line.strip().split()  # 默认空白符分割， 有点牛逼哦
                    cmd = user_in.pop(0)
                    parameters = user_in
                    self.__execute(cmd, parameters)
                f.close()
            else:
                self.__execute(cmd, parameters)

    def __execute(self, cmd, parameters):
        if cmd not in self.cmd_set.keys():
            print('Command not found. Please try again.')
            return
        func = self.cmd_set[cmd]
        if func is None:
            return
        func(parameters)

    def cr(self, par):
        if len(par) != 2:
            print("Input is illegal. Please try again.")
            return
        pName = par[0]
        priority = int(par[1])
        if priority not in [0, 1, 2]:
            print("Priority is illegal. Please try again.")
            return
        fPro = self.get_runningP()
        newP = PCB(self.pCnt, 'ready', self.RL, priority, pName, fPro)
        self.pCnt += 1

        self.__generate_tree(fPro, newP)
        if self.RL[newP.priority] is None:
            self.RL[newP.priority] = newP
        else:
            tmp = self.RL[newP.priority]
            while tmp.pNext is not None:
                tmp = tmp.pNext
            tmp.pNext = newP
            newP.pPre = tmp
        self.schedule()

    def __generate_tree(self, fpcb: PCB, pcb: PCB):
        if fpcb.son is None:
            fpcb.son = pcb
        else:
            tmp = fpcb.son
            while tmp.brother is not None:
                tmp = tmp.brother
            tmp.brother = pcb

    def schedule(self):
        pNow = self.get_runningP()  # running/ready process
        pHigh = None
        for pri in range(2, -1, -1):
            if self.RL[pri] is not None:
                pHigh = self.RL[pri]
                break

        if pNow is None:
            pHigh.st = 'running'
            return
        if pNow.priority < pHigh.priority:
            pHigh.st = 'running'
            if pHigh.pid != self.RL[pHigh.priority].pid:
                pHigh.pNext = self.RL[pHigh.priority]
                self.RL[pHigh.priority] = pHigh  # 换头
            pNow.st = 'ready'

    def de(self, par):
        del_pid = self.__get_pid(par[0])
        for pri in [2, 1]:
            tmp = self.RL[pri]
            while tmp is not None:
                if tmp.pid == del_pid:
                    fbro = self.__get_forward_brother(tmp.parent, tmp)
                    if fbro is not None:
                        fbro.brother = tmp.brother
                    else:
                        tmp.parent.son = None
                    self.__kill_tree(tmp)
                    self.__wake()
                    self.schedule()
                    return
                tmp = tmp.pNext

        # in blocked list
        for bp in self.BL:
            if bp.pid == del_pid:
                fbro = self.__get_forward_brother(bp.parent, bp)
                if fbro is not None:
                    fbro.brother = bp.brother
                else:
                    bp.parent.son = None
                self.__kill_tree(bp)
                break
        self.__wake()
        self.schedule()

    def __get_forward_brother(self, fpcb: PCB, son: PCB):
        forward_son = fpcb.son
        if fpcb is None or son is None:
            return
        if son.pid == forward_son.pid:
            return None
        while forward_son.brother.pid != son.pid:
            forward_son = forward_son.brother
        # must have
        return forward_son

    def __get_pid(self, pName):
        for pri in [2, 1]:
            tmp = self.RL[pri]
            while tmp is not None:
                if tmp.pName == pName:
                    return tmp.pid
                else:
                    tmp = tmp.pNext
        for bp in self.BL:
            if bp.pName == pName:
                return bp.pid

    def __kill_tree(self, pcb: PCB):
        if pcb is None:
            return
        for rid in pcb.occupied:  # delete resource
            rcb = self.__get_CB(self.resources, rid, 'rcb')
            rcb.release(pcb)  # update both pcb and rcb
        pcb.delete()

        self.__kill_tree(pcb.son)
        if pcb.son is not None:
            tmp = pcb.son.brother
            while tmp is not None:
                self.__kill_tree(tmp)
                tmp = tmp.brother

    def __get_CB(self, cbList, id, t):
        res = None
        if t == 'pcb':
            for cb in cbList:
                if cb.pid == id:
                    res = cb
                    break
        else:
            for cb in cbList:
                if cb.rid == id:
                    res = cb
                    break
        return res

    def req(self, par: list):
        pNow = self.get_runningP()
        if len(par) != 2:
            print("Input is illegal. Please try again.")
            return
        rName = par[0]
        req_Num = int(par[1])

        # 一次只申请一个资源
        rcb = next(filter(lambda r: r.rName == rName,
                          self.resources), None)
        if rcb is None:
            print("No resource was found")
            return
        if req_Num <= rcb.remain and pNow.st == 'running':
            rcb.insert(pNow.pid, req_Num)
            pNow.insert(rcb.rid)
        else:  # blocked
            if req_Num > rcb.N:
                print("Request denied: out of bound")
                return
            rcb.block(pNow.pid)  # blocked on resource
            pNow.st = 'blocked'  # must running -> blocked
            pNow.sl[pNow.priority] = pNow.pNext
            pNow.block(rcb.rid, req_Num)  # resource blocked list

            # relink RB. pNow at head
            if pNow.pNext is not None:
                pNow.pNext.pPre = None
            self.RL[pNow.priority] = pNow.pNext
            pNow.pPre = None
            pNow.pNext = None
            self.BL.append(pNow)  # save pointer for list block
            self.schedule()

    def rel(self, par):
        pNow = self.get_runningP()
        if len(par) != 2:
            print("Input is illegal. Please try again.")
            return
        rName = par[0]
        rel_Num = int(par[1])
        rcb = next(filter(lambda r: r.rName == rName,
                          self.resources), None)
        if rcb is None:
            print("No resource was found")
            return
        elif pNow.pid not in rcb.occupy_list.keys():
            print(pNow.pName + "doesn't have " + rcb.rName)
            return

        if rcb.occupy_list[pNow.pid] >= rel_Num:
            rcb.release(pNow, rel_Num)  # 同时判断是否释放pcb.occupied
            self.__wake()  # wake up other processes
            self.schedule()
        else:
            print("Release denied: out of bound")

    def __wake(self):
        # get available vector
        available_vector = {}
        for rcb in self.resources:
            if rcb.remain != 0:
                available_vector[rcb.rid] = rcb.remain
        del_list = []
        for pcb_ind in range(len(self.BL)):
            pcb = self.BL[pcb_ind]
            N = len(pcb.sl)
            for rid in pcb.sl:
                if rid in available_vector.keys() and \
                        pcb.blocked_res[rid] <= available_vector[rid]:
                    N -= 1
            # satisfy the condition
            if N != 0:
                continue
            for rid in pcb.sl:
                rcb = self.__get_CB(self.resources, rid, t='rcb')
                req_num = pcb.blocked_res[rid]
                rcb.insert(pcb.pid, req_num)
                pcb.insert(rcb.rid)
            pcb.sl = self.RL
            pcb.st = 'ready'
            pcb.blocked_res = {}
            # insert to RL
            if self.RL[pcb.priority] is None:
                self.RL[pcb.priority] = pcb
            else:
                tmp = self.RL[pcb.priority]
                while tmp.pNext is not None:
                    tmp = tmp.pNext
                tmp.pNext = pcb
                pcb.pPre = tmp
            del_list.append(pcb_ind)
        # remove from BL once
        # can't del self.BL[pcb_ind]
        for i in del_list:
            del self.BL[i]

    def to(self, par):
        pNow = self.get_runningP()
        if pNow.pid == 0:
            return
        # pNow can use system call so it must be a running process.
        if pNow.pNext is None:  # exit
            pass
            # pNow.delete(pNow.sl)
            # print(pNow.pName + '--' + str(pNow.pid) + " exit")
        else:
            tmp = pNow.pNext
            while tmp.pNext is not None:
                tmp = tmp.pNext
            pNow.sl[pNow.priority] = pNow.pNext
            pNow.pNext.pPre = None
            tmp.pNext = pNow
            pNow.pPre = tmp
            pNow.pNext = None
            pNow.st = 'ready'

        self.schedule()

    def list(self, par):
        if len(par) != 1:
            print("Input is illegal. Please try again.")
            return
        par = par[0]
        if par == 'ready':
            out = self.iter_list(self.RL)
            print(out)
        elif par == 'block' or par == 'b':
            out = self.iter_list(self.BL)
            print(out)
        elif par == 'res':
            out = 'resources:'
            for Ri in self.resources:
                out += '\nR' + str(Ri.rid) + ':' + str(Ri.remain)
            print(out)
        else:
            print("Parameters error")

    def exit(self, par):
        self.flag = False
        print('Shell is terminated', end='')
        exit()

    def get_runningP(self):  # running 放在队头
        p = None
        for pri in range(2, -1, -1):
            if self.RL[pri] is not None:
                if self.RL[pri].st == 'running':
                    # detective running p
                    return self.RL[pri]
                # elif self.RL[pri].st == 'ready' and priHigh < pri:
                #     # detective highest ready
                #     priHigh = pri
                #     p = self.RL[pri]
        return p

    def iter_list(self, d):
        res = '\nready list:'
        if type(d) == dict:
            for pri in range(2, -1, -1):
                tmp = d[pri]
                res += '\n' + str(pri) + ': '
                while tmp is not None:
                    res += tmp.pName + ':' + tmp.st + ' '
                    tmp = tmp.pNext
        else:
            res = '\nblocked list:'
            res += '\n'
            for p in d:
                res += p.pName + '  '
        return res


class Timer(Thread):
    def __init__(self, interval, s: YShell):
        Thread.__init__(self)
        self.interval = interval
        self.start_time = time.time()
        self.s = s

    def run(self) -> None:
        while s.flag:
            if time.time() - self.start_time - self.interval > 0:
                self.start_time = time.time()
                s.to([])


if __name__ == "__main__":
    s = YShell()
    t = Timer(s=s, interval=2)
    print("Process init is already running\nUse 'exit' command to exit")
    try:
        s.run()
    except KeyboardInterrupt as e:
        print('\b\b\b\b\b\b\b\b\b\bShell is terminated', end='')
