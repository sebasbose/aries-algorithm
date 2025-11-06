"""
Simulador del Algoritmo ARIES
Laboratorio 3 - Bases de Datos Avanzadas

Autor: Sebastián Bolaños Serrano
Fecha: 06 de Noviembre 2025
"""

import re
import os
import sys
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import time


class OperationType(Enum):
    START = "START"
    WRITE = "WRITE"
    COMMIT = "COMMIT"
    ABORT = "ABORT"
    CHECKPOINT = "CHECKPOINT"
    CRASH = "CRASH"


@dataclass
class LogEntry:
    """Representa una entrada en el log"""
    lsn: int  # Log Sequence Number
    timestamp: int
    transaction_id: str
    operation: OperationType
    page: str = None
    old_value: int = None
    new_value: int = None

    def __str__(self):
        if self.operation == OperationType.WRITE:
            return f"LSN:{self.lsn} T{self.timestamp} <{self.transaction_id}, {self.page}, {self.old_value}, {self.new_value}>"
        elif self.operation in [OperationType.START, OperationType.COMMIT, OperationType.ABORT]:
            return f"LSN:{self.lsn} T{self.timestamp} <{self.operation.value} {self.transaction_id}>"
        else:
            return f"LSN:{self.lsn} T{self.timestamp} <{self.operation.value}>"


class Database:
    """Simula una base de datos con páginas"""
    def __init__(self):
        self.pages: Dict[str, int] = {}
        self.dirty_pages: Set[str] = set()
    
    def write(self, page: str, value: int):
        self.pages[page] = value
        self.dirty_pages.add(page)
    
    def read(self, page: str) -> int:
        return self.pages.get(page, 0)
    
    def initialize_page(self, page: str, value: int):
        if page not in self.pages:
            self.pages[page] = value


class ARIESRecovery:
    """Implementación del algoritmo ARIES"""
    
    def __init__(self):
        self.log: List[LogEntry] = []
        self.database = Database()
        self.transaction_table: Dict[str, Dict] = {}
        self.dirty_page_table: Dict[str, int] = {}
        self.lsn_counter = 0
        self.crash_point = -1
        
    def parse_log_file(self, filename: str) -> List[LogEntry]:
        """Lee y parsea el archivo de log"""
        entries = []
        lsn = 0
        
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                entry = self._parse_log_line(line, lsn)
                if entry:
                    entries.append(entry)
                    lsn += 1
                    
                    if entry.operation == OperationType.CRASH:
                        self.crash_point = lsn - 1
                        break
        
        return entries
    
    def _parse_log_line(self, line: str, lsn: int) -> LogEntry:
        """Parsea una línea del log"""
        line = line.strip('<>')
        
        # CRASH
        if 'CRASH' in line.upper():
            return LogEntry(lsn, lsn, None, OperationType.CRASH)
        
        # START
        match = re.match(r'START\s+(\w+)', line, re.IGNORECASE)
        if match:
            tid = match.group(1)
            return LogEntry(lsn, lsn, tid, OperationType.START)
        
        # COMMIT
        match = re.match(r'COMMIT\s+(\w+)', line, re.IGNORECASE)
        if match:
            tid = match.group(1)
            return LogEntry(lsn, lsn, tid, OperationType.COMMIT)
        
        # ABORT
        match = re.match(r'ABORT\s+(\w+)', line, re.IGNORECASE)
        if match:
            tid = match.group(1)
            return LogEntry(lsn, lsn, tid, OperationType.ABORT)
        
        # WRITE: <T1, A, 100, 200>
        match = re.match(r'(\w+),\s*(\w+),\s*(\d+),\s*(\d+)', line)
        if match:
            tid = match.group(1)
            page = match.group(2)
            old_val = int(match.group(3))
            new_val = int(match.group(4))
            return LogEntry(lsn, lsn, tid, OperationType.WRITE, page, old_val, new_val)
        
        return None
    
    def analysis_phase(self) -> Tuple[Set[str], Set[str]]:
        """
        Fase 1: ANÁLISIS
        Identifica transacciones activas y páginas sucias al momento del crash
        """
        active_transactions = set()
        committed_transactions = set()
        self.transaction_table.clear()
        self.dirty_page_table.clear()
        
        for entry in self.log:
            if entry.operation == OperationType.CRASH:
                break
            
            if entry.operation == OperationType.START:
                active_transactions.add(entry.transaction_id)
                self.transaction_table[entry.transaction_id] = {
                    'status': 'active',
                    'lastLSN': entry.lsn
                }
            
            elif entry.operation == OperationType.WRITE:
                if entry.page not in self.dirty_page_table:
                    self.dirty_page_table[entry.page] = entry.lsn
                
                self.database.initialize_page(entry.page, entry.old_value)
                
                if entry.transaction_id in self.transaction_table:
                    self.transaction_table[entry.transaction_id]['lastLSN'] = entry.lsn
            
            elif entry.operation == OperationType.COMMIT:
                if entry.transaction_id in active_transactions:
                    active_transactions.remove(entry.transaction_id)
                    committed_transactions.add(entry.transaction_id)
                    self.transaction_table[entry.transaction_id]['status'] = 'committed'
            
            elif entry.operation == OperationType.ABORT:
                if entry.transaction_id in active_transactions:
                    active_transactions.remove(entry.transaction_id)
                    self.transaction_table[entry.transaction_id]['status'] = 'aborted'
        
        losers = active_transactions - committed_transactions
        
        return committed_transactions, losers
    
    def redo_phase(self):
        """
        Fase 2: REDO
        Repite todas las operaciones de escritura desde el checkpoint
        """
        for entry in self.log:
            if entry.operation == OperationType.CRASH:
                break
            
            if entry.operation == OperationType.WRITE:
                self.database.write(entry.page, entry.new_value)
    
    def undo_phase(self, losers: Set[str]):
        """
        Fase 3: UNDO
        Deshace todas las operaciones de transacciones no comprometidas
        """
        if not losers:
            return
        
        undo_operations = []
        for entry in reversed(self.log):
            if entry.operation == OperationType.CRASH:
                continue
            if entry.operation == OperationType.WRITE and entry.transaction_id in losers:
                undo_operations.append(entry)
        
        for entry in undo_operations:
            self.database.write(entry.page, entry.old_value)
    
    def recover(self, log_file: str):
        """Ejecuta el proceso completo de recuperación ARIES"""
        print(f"\n{os.path.basename(log_file)}")
        print("=" * 50)
        
        self.log = self.parse_log_file(log_file)
        
        winners, losers = self.analysis_phase()
        self.redo_phase()
        self.undo_phase(losers)
        
        print("\nEstado final:")
        for page in sorted(self.database.pages.keys()):
            print(f"  {page} = {self.database.pages[page]}")
        
        return self.database.pages


if __name__ == "__main__":
    print("SIMULADOR DEL ALGORITMO ARIES")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Uso: python aries.py <archivo_log.txt>")
        sys.exit(1)
    
    log_file = sys.argv[1]
    
    if not os.path.exists(log_file):
        print(f"Error: El archivo '{log_file}' no existe")
        sys.exit(1)
    
    recovery = ARIESRecovery()
    final_state = recovery.recover(log_file)