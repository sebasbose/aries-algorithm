"""
Simulador del Algoritmo ARIES
Laboratorio 3 - Bases de Datos Avanzadas

Autor: Sebastián Bolaños Serrano
Fecha: 06 de Noviembre 2025
"""

import os
import sys

class ARIESRecovery:
    def __init__(self):
        self.log = []
        self.pages = {}
        self.active_txns = set()
        self.committed_txns = set()
        self.stats = {
            'total_operations': 0,
            'write_operations': 0,
            'undo_operations': 0,
            'pages_affected': set(),
            'initial_state': {},
            'crash_detected': False
        }
    
    def parse_log(self, filename):
        entries = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                entries.append(line)
                self.stats['total_operations'] += 1
                if 'CRASH' in line.upper():
                    self.stats['crash_detected'] = True
                    break
        return entries
    
    def analysis(self):
        # Find active and committed transactions
        for line in self.log:
            if 'START' in line:
                tid = line.split()[1].rstrip('>')
                self.active_txns.add(tid)
            elif 'COMMIT' in line:
                tid = line.split()[1].rstrip('>')
                self.committed_txns.add(tid)
                if tid in self.active_txns:
                    self.active_txns.remove(tid)
            elif 'WRITE' in line or ',' in line:
                # Parse write operation
                parts = line.strip('<>').split(',')
                if len(parts) >= 4:
                    tid = parts[0].strip()
                    page = parts[1].strip()
                    old_val = int(parts[2].strip())
                    new_val = int(parts[3].strip())
                    self.stats['write_operations'] += 1
                    self.stats['pages_affected'].add(page)
                    if page not in self.pages:
                        self.pages[page] = old_val
                        self.stats['initial_state'][page] = old_val
        
        losers = self.active_txns - self.committed_txns
        return self.committed_txns, losers
    
    def redo(self):
        # Redo all operations
        for line in self.log:
            if 'WRITE' in line or (',' in line and '<' in line):
                parts = line.strip('<>').split(',')
                if len(parts) >= 4:
                    page = parts[1].strip()
                    new_val = int(parts[3].strip())
                    self.pages[page] = new_val
    
    def undo(self, losers):
        # Undo operations from loser transactions
        undo_ops = []
        for line in reversed(self.log):
            if 'WRITE' in line or (',' in line and '<' in line):
                parts = line.strip('<>').split(',')
                if len(parts) >= 4:
                    tid = parts[0].strip()
                    if tid in losers:
                        page = parts[1].strip()
                        old_val = int(parts[2].strip())
                        undo_ops.append((page, old_val))
                        self.stats['undo_operations'] += 1
        
        for page, old_val in undo_ops:
            self.pages[page] = old_val
    
    
    def generar_conclusiones(self, winners, losers):
        print("\n" + "="*50)
        print("ARIES PROCESS CONCLUSIONS")
        print("="*50)
        
        # Transaction analysis
        print(f"\nTRANSACTIONS:")
        print(f"  - Winner transactions (committed): {len(winners)}")
        if winners:
            print(f"    Transactions: {', '.join(sorted(winners))}")
        print(f"  - Loser transactions (aborted): {len(losers)}")
        if losers:
            print(f"    Transactions: {', '.join(sorted(losers))}")
        
        # Operation statistics
        print(f"\nOPERATION STATISTICS:")
        print(f"  - Total operations in log: {self.stats['total_operations']}")
        print(f"  - Write operations: {self.stats['write_operations']}")
        print(f"  - UNDO operations applied: {self.stats['undo_operations']}")
        print(f"  - Pages affected: {len(self.stats['pages_affected'])}")
        if self.stats['pages_affected']:
            print(f"    Pages: {', '.join(sorted(self.stats['pages_affected']))}")
        
        # State analysis
        print(f"\nSTATE ANALYSIS:")
        print("  Initial vs final state:")
        for page in sorted(self.pages.keys()):
            inicial = self.stats['initial_state'].get(page, 0)
            final = self.pages[page]
            cambio = "✓" if inicial != final else "="
            print(f"    {page}: {inicial} -> {final} [{cambio}]")
        
        # Performance and optimization
        print(f"\nPERFORMANCE:")
        eficiencia = ((self.stats['write_operations'] - self.stats['undo_operations']) / 
                     max(self.stats['write_operations'], 1)) * 100
        print(f"  - Process efficiency: {eficiencia:.1f}%")
        print(f"  - Crash detected: {'Yes' if self.stats['crash_detected'] else 'No'}")
        
        if self.stats['undo_operations'] > 0:
            print(f"  - UNDO overhead: {self.stats['undo_operations']} operations reverted")
        else:
            print("  - No UNDO overhead (all transactions committed)")
        
        print(f"\nOPTIMIZATION:")
        if len(losers) > len(winners):
            print("  - RECOMMENDATION: Many loser transactions detected")
            print("    Consider improving transaction handling to reduce rollbacks")
        elif self.stats['undo_operations'] == 0:
            print("  - OPTIMAL: No UNDO operations required")
        else:
            print("  - ACCEPTABLE: Standard recovery process executed")

    def recover(self, log_file):
        print(f"\n{os.path.basename(log_file)}")
        print("=" * 50)
        
        self.log = self.parse_log(log_file)
        winners, losers = self.analysis()
        self.redo()
        self.undo(losers)
        
        print("\nLog content:")
        for i, line in enumerate(self.log):
            print(f"  [{i}] {line}")
        
        print("\nFinal state:")
        for page in sorted(self.pages.keys()):
            print(f"  {page} = {self.pages[page]}")
        
        # Generate conclusions
        self.generar_conclusiones(winners, losers)
        
        return self.pages


if __name__ == "__main__":
    print("ARIES Simulator")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python aries.py <log_file.txt>")
        sys.exit(1)
    
    log_file = sys.argv[1]
    
    if not os.path.exists(log_file):
        print(f"Error: File '{log_file}' does not exist")
        sys.exit(1)
    
    recovery = ARIESRecovery()
    final_state = recovery.recover(log_file)