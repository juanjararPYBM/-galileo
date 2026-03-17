#!/usr/bin/env python3
"""
Galileo Security Logger
Registra todas las operaciones de MCP para auditoría.
"""

import json
import os
from datetime import datetime
from pathlib import Path

class SecurityLogger:
    """Logger de operaciones de seguridad"""
    
    def __init__(self, log_dir='/home/user/.openclaw/workspace/logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivos de log separados
        self.files = {
            'filesystem': open(self.log_dir / 'filesystem.log', 'a'),
            'fetch': open(self.log_dir / 'fetch.log', 'a'),
            'git': open(self.log_dir / 'git.log', 'a'),
            'sqlite': open(self.log_dir / 'sqlite.log', 'a'),
            'security': open(self.log_dir / 'security.log', 'a'),
            'blocked': open(self.log_dir / 'blocked.log', 'a'),
        }
        
        # Formato de log
        self.format = lambda mcp, action, details: json.dumps({
            'timestamp': datetime.now().isoformat(),
            'mcp': mcp,
            'action': action,
            **details
        }) + '\n'
    
    def log(self, mcp, action, allowed, details):
        """Registra una operación"""
        # Escribir al log específico
        if mcp in self.files:
            self.files[mcp].write(self.format(mcp, action, details))
            self.files[mcp].flush()
        
        # Si fue bloqueada, también escribir en blocked.log
        if not allowed:
            self.files['blocked'].write(self.format(mcp, action, {
                **details,
                'BLOCKED': True,
                'reason': details.get('error', 'Unknown')
            }))
            self.files['blocked'].flush()
            
            # Escribir en security.log también
            self.files['security'].write(self.format(mcp, action, {
                **details,
                'severity': 'CRITICAL' if not allowed else 'INFO'
            }))
            self.files['security'].flush()
        
        # Siempre escribir en security.log
        self.files['security'].write(self.format(mcp, action, details))
        self.files['security'].flush()
    
    def close(self):
        """Cierra todos los archivos"""
        for f in self.files.values():
            f.close()
    
    def get_summary(self, days=7):
        """Obtiene un resumen de los últimos N días"""
        summary = {
            'total_operations': 0,
            'blocked_operations': 0,
            'by_mcp': {},
            'by_action': {},
            'recent_blocks': []
        }
        
        # Leer logs de security
        security_log = self.log_dir / 'security.log'
        if not security_log.exists():
            return summary
        
        with open(security_log, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    summary['total_operations'] += 1
                    
                    mcp = entry.get('mcp', 'unknown')
                    summary['by_mcp'][mcp] = summary['by_mcp'].get(mcp, 0) + 1
                    
                    action = entry.get('action', 'unknown')
                    summary['by_action'][action] = summary['by_action'].get(action, 0) + 1
                    
                    if entry.get('BLOCKED'):
                        summary['blocked_operations'] += 1
                        summary['recent_blocks'].append(entry)
                
                except json.JSONDecodeError:
                    continue
        
        # Limitar recent_blocks a últimos 10
        summary['recent_blocks'] = summary['recent_blocks'][-10:]
        
        return summary


# Instancia global
logger = SecurityLogger()


def log_operation(mcp, operation, params, result):
    """
    Registra una operación de MCP.
    
    Args:
        mcp: Nombre del MCP
        operation: Operación realizada
        params: Parámetros de la operación
        result: Resultado de la validación
    """
    details = {
        'operation': operation,
        'params': params,
        'allowed': result.get('allowed', False),
        'message': result.get('message', ''),
    }
    
    if not result.get('allowed'):
        details['error'] = result.get('message', 'Blocked by security')
    
    logger.log(mcp, operation, result.get('allowed', False), details)


if __name__ == "__main__":
    # Test
    print("=== Security Logger Test ===\n")
    
    # Simular operaciones
    log_operation(
        'filesystem',
        'read_text_file',
        {'path': '/home/user/.openclaw/workspace/data/test.csv'},
        {'allowed': True}
    )
    
    log_operation(
        'filesystem',
        'read_text_file',
        {'path': '~/.ssh/id_rsa'},
        {'allowed': False, 'message': 'LECTURA BLOQUEADA: Path ~/.ssh/id_rsa coincide con patrón bloqueado: **/.ssh/**'}
    )
    
    log_operation(
        'fetch',
        'fetch',
        {'url': 'https://github.com/anthropic/claude-code'},
        {'allowed': True}
    )
    
    # Obtener resumen
    summary = logger.get_summary()
    print("Resumen:")
    print(f"  Total operaciones: {summary['total_operations']}")
    print(f"  Operaciones bloqueadas: {summary['blocked_operations']}")
    print(f"  Por MCP: {summary['by_mcp']}")
    print(f"  Por acción: {summary['by_action']}")
    
    logger.close()
    print("\n✅ Logger funcionando correctamente")
