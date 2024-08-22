from enum import Enum
import uuid
from collections import deque

# Enum para os estados do processo
class ProcessState(Enum):
    READY = "pronto"
    RUNNING = "executando"
    BLOCKED = "bloqueado"
    TERMINATED = "terminado"

# Classe para representar um processo
class Process:
    def __init__(self, pid, instructions):
        self.pid = pid  # Process Identifier
        self.state = ProcessState.READY  # Estado inicial do processo
        self.pc = 0  # Contador de Programa
        self.registers = {}  # Registros
        self.memory = {}  # Memória alocada
        self.instructions = instructions  # Instruções do processo

    def execute_instruction(self):
        if self.pc < len(self.instructions):
            instruction = self.instructions[self.pc]
            self.pc += 1
            return instruction
        return None

# Classe para gerenciar processos
class ProcessManager:
    def __init__(self):
        self.processes = {}

    def create_process(self, instructions):
        pid = str(uuid.uuid4())  # Gera um identificador único para o processo
        process = Process(pid, instructions)
        self.processes[pid] = process
        return pid

    def terminate_process(self, pid):
        if pid in self.processes:
            self.processes[pid].state = ProcessState.TERMINATED
            del self.processes[pid]

    def get_process(self, pid):
        return self.processes.get(pid, None)

    def update_process_state(self, pid, state):
        if pid in self.processes:
            self.processes[pid].state = state

# Classe do escalonador
class Scheduler:
    def __init__(self, algorithm="FIFO"):
        self.ready_queue = deque()
        self.algorithm = algorithm

    def add_process(self, process):
        self.ready_queue.append(process)

    def get_next_process(self):
        if not self.ready_queue:
            return None

        if self.algorithm == "FIFO":
            return self.ready_queue.popleft()
        elif self.algorithm == "RoundRobin":
            process = self.ready_queue.popleft()
            self.ready_queue.append(process)
            return process
        elif self.algorithm == "SJF":
            # Ordenar por tamanho das instruções para Shortest Job First (SJF)
            self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: len(p.instructions)))
            return self.ready_queue.popleft()
        else:
            raise ValueError("Algoritmo de escalonamento desconhecido")

    def remove_process(self, pid):
        self.ready_queue = deque(p for p in self.ready_queue if p.pid != pid)

# Classe da Máquina Virtual
class VirtualMachine:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.process_manager = ProcessManager()

    def execute(self):
        while True:
            process = self.scheduler.get_next_process()
            if process is None:
                break  # Não há mais processos para executar
            
            process.state = ProcessState.RUNNING
            instruction = process.execute_instruction()
            
            if instruction is not None:
                self.execute_instruction(process, instruction)
            else:
                self.process_manager.terminate_process(process.pid)

    def execute_instruction(self, process, instruction):
        print(f"Executando: {instruction} no processo {process.pid}")

if __name__ == "__main__":
    # Instruções para o primeiro processo
    instructions1 = [
        "LOAD_SCENE 'initial_scene.txt'",
        "DRAW_SCENE",
        "CREATE_CHARACTER 'hero', 'hero_sprite.png', 100, 100",
        "MOVE_CHARACTER 'hero', 'UP', 10"
    ]

    # Instruções para o segundo processo
    instructions2 = [
        "LOAD_SCENE 'battle_scene.txt'",
        "DRAW_SCENE",
        "CREATE_CHARACTER 'enemy', 'enemy_sprite.png', 200, 200",
        "MOVE_CHARACTER 'enemy', 'LEFT', 5"
    ]

    # Inicializando a VM e criando processos
    scheduler = Scheduler(algorithm="RoundRobin")
    vm = VirtualMachine(scheduler)

    # Criando e adicionando o primeiro processo
    pid1 = vm.process_manager.create_process(instructions1)
    process1 = vm.process_manager.get_process(pid1)
    scheduler.add_process(process1)

    # Criando e adicionando o segundo processo
    pid2 = vm.process_manager.create_process(instructions2)
    process2 = vm.process_manager.get_process(pid2)
    scheduler.add_process(process2)

    # Executando a VM
    vm.execute()
