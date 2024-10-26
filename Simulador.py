import time
from enum import Enum
import uuid
from collections import deque
from random import randint

# Enum para os estados do processo
class ProcessState(Enum):
    READY = "pronto"
    RUNNING = "executando"
    BLOCKED = "bloqueado"
    TERMINATED = "terminado"

# Classe para representar um processo
class Process:
    def _init_(self, pid, instructions):
        self.pid = pid
        self.state = ProcessState.READY
        self.pc = 0
        self.instructions = instructions
        self.memory_used = randint(1, 10)  # Simulando uso de memória
        self.in_memory = True

    def execute_instruction(self):
        if self.pc < len(self.instructions):
            instruction = self.instructions[self.pc]
            self.pc += 1
            return instruction
        return None

# Classe para gerenciar processos
class ProcessManager:
    def _init_(self, max_memory):
        self.processes = {}
        self.max_memory = max_memory
        self.current_memory = 0
        self.virtual_memory = deque()

    def create_process(self, instructions):
        pid = str(uuid.uuid4())
        process = Process(pid, instructions)
        self.processes[pid] = process
        return pid

    def get_process(self, pid):
        return self.processes.get(pid, None)

    def terminate_process(self, pid):
        if pid in self.processes:
            process = self.processes[pid]
            self.current_memory -= process.memory_used
            del self.processes[pid]

    def manage_memory(self, process):
        if self.current_memory + process.memory_used > self.max_memory:
            self.move_to_virtual_memory()
        self.current_memory += process.memory_used

    def move_to_virtual_memory(self):
        process = self.find_least_recently_used()
        if process:
            process.in_memory = False
            self.current_memory -= process.memory_used
            self.virtual_memory.append(process)
            print(f"Processo {process.pid} movido para memória virtual.")
            time.sleep(1)  # Simulação de atraso na cópia

    def find_least_recently_used(self):
        for process in self.processes.values():
            if process.in_memory:
                return process
        return None

# Classe do escalonador com filas hierárquicas
class HierarchicalScheduler:
    def _init_(self):
        self.high_priority_queue = deque()
        self.low_priority_queue = deque()

    def add_process(self, process, priority="low"):
        if priority == "high":
            self.high_priority_queue.append(process)
        else:
            self.low_priority_queue.append(process)

    def get_next_process(self):
        if self.high_priority_queue:
            return self.high_priority_queue.popleft()
        elif self.low_priority_queue:
            process = self.low_priority_queue.popleft()
            self.low_priority_queue.append(process)
            return process
        return None

# Classe da Máquina Virtual
class VirtualMachine:
    def _init_(self, scheduler, max_memory):
        self.scheduler = scheduler
        self.process_manager = ProcessManager(max_memory)

    def execute(self):
        while True:
            process = self.scheduler.get_next_process()
            if process is None:
                break
            
            if not process.in_memory:
                self.load_from_virtual_memory(process)

            process.state = ProcessState.RUNNING
            instruction = process.execute_instruction()

            if instruction is not None:
                self.execute_instruction(process, instruction)
            else:
                print(f"Processo {process.pid} terminado.")
                self.process_manager.terminate_process(process.pid)

    def execute_instruction(self, process, instruction):
        print(f"Executando: {instruction} no processo {process.pid}")

    def load_from_virtual_memory(self, process):
        process.in_memory = True
        self.process_manager.current_memory += process.memory_used
        print(f"Carregando processo {process.pid} da memória virtual para a memória principal.")
        time.sleep(1)  # Simulação de atraso

# Função principal para o terminal de comando
def main():
    scheduler = HierarchicalScheduler()
    vm = VirtualMachine(scheduler, max_memory=20)  # Memória máxima de 20 unidades

    while True:
        command = input("\nDigite um comando (criar, listar, executar, terminar, sair): ").strip().lower()
        
        if command == "criar":
            instructions = input("Digite as instruções separadas por vírgula: ").split(',')
            priority = input("Prioridade do processo (alta/baixa): ").strip().lower()
            pid = vm.process_manager.create_process(instructions)
            process = vm.process_manager.get_process(pid)
            vm.process_manager.manage_memory(process)
            scheduler.add_process(process, priority="high" if priority == "alta" else "low")
            print(f"Processo {pid} criado com sucesso.")

        elif command == "listar":
            print("Processos Atuais:")
            for pid, process in vm.process_manager.processes.items():
                print(f"PID: {pid}, Estado: {process.state.value}, Memória Usada: {process.memory_used}, Na Memória: {'Sim' if process.in_memory else 'Não'}")

        elif command == "executar":
            print("Iniciando execução dos processos...")
            vm.execute()
            print("Execução dos processos finalizada.")

        elif command == "terminar":
            pid = input("Digite o PID do processo a ser terminado: ").strip()
            if pid in vm.process_manager.processes:
                vm.process_manager.terminate_process(pid)
                print(f"Processo {pid} terminado.")
            else:
                print(f"Processo com PID {pid} não encontrado.")

        elif command == "sair":
            print("Encerrando o terminal.")
            break

        else:
            print("Comando não reconhecido. Tente novamente.")

if __name__ == "_main_":
    main()
