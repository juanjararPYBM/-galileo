#!/usr/bin/env python3
"""
Galileo Security Validator
Valida todas las operaciones de MCP para asegurar que son seguras.
"""

import os
import fnmatch
import json
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/.openclaw/workspace/logs/security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Excepción de seguridad"""
    pass


class PathValidator:
    """Validador de rutas para el Filesystem MCP"""
    
    def __init__(self, config_path='/home/user/.openclaw/workspace/config/security.json'):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.allowed_dirs = self.config['filesystem']['allowed_directories']
        self.blocked_patterns = self.config['filesystem']['blocked_patterns']
        self.readonly_exts = self.config['filesystem']['readonly_extensions']
    
    def normalize_path(self, path):
        """Normaliza y resuelve el path"""
        # Expande ~ al home
        if path.startswith('~'):
            path = os.path.expanduser(path)
        # Resuelve path absoluto
        return os.path.normpath(os.path.abspath(path))
    
    def is_path_allowed(self, path):
        """Verifica si el path está en la lista de permitidos"""
        normalized = self.normalize_path(path)
        
        # Verificar en allowed directories
        for allowed_dir in self.allowed_dirs:
            allowed_normalized = self.normalize_path(allowed_dir)
            if normalized.startswith(allowed_normalized):
                return True, None
        
        return False, f"Path {path} no está en directorios permitidos"
    
    def is_path_blocked(self, path):
        """Verifica si el path coincide con patrones bloqueados"""
        normalized = self.normalize_path(path)
        
        for pattern in self.blocked_patterns:
            # Convertir patrón glob a path
            if pattern.startswith('**/'):
                pattern = pattern[3:]
            
            if fnmatch.fnmatch(normalized, pattern):
                return True, f"Path {path} coincide con patrón bloqueado: {pattern}"
            
            # También verificar el nombre del archivo
            filename = os.path.basename(normalized)
            if fnmatch.fnmatch(filename, pattern.replace('**/', '')):
                return True, f"Archivo {filename} coincide con patrón bloqueado: {pattern}"
        
        return False, None
    
    def validate_read(self, path):
        """Valida si se puede leer un archivo"""
        normalized = self.normalize_path(path)
        
        # 1. Verificar que está en directorios permitidos
        allowed, error = self.is_path_allowed(path)
        if not allowed:
            logger.warning(f"LECTURA DENEGADA: {error}")
            raise SecurityError(f"LECTURA DENEGADA: {error}")
        
        # 2. Verificar patrones bloqueados
        blocked, error = self.is_path_blocked(path)
        if blocked:
            logger.critical(f"LECTURA BLOQUEADA: {error}")
            raise SecurityError(f"LECTURA BLOQUEADA: {error}")
        
        # 3. Registrar operación
        logger.info(f"LECTURA PERMITIDA: {path}")
        return True
    
    def validate_write(self, path):
        """Valida si se puede escribir un archivo"""
        # Primero validar como lectura
        self.validate_read(path)
        
        # 2. Verificar extensión de solo lectura
        ext = os.path.splitext(path)[1]
        if ext in self.readonly_exts:
            raise SecurityError(f"ESCRITURA DENEGADA: Archivos {ext} son de solo lectura")
        
        # 3. Si existe, es un archivo de configuración?
        if os.path.exists(path):
            filename = os.path.basename(path)
            if filename in ['security.json', 'config.json', 'mcporter.json']:
                logger.warning(f"Intentando sobreescribir archivo de configuración: {path}")
                raise SecurityError(f"ESCRITURA DENEGADA: No se puede sobreescribir {filename}")
        
        # 4. Registrar operación
        logger.info(f"ESCRITURA PERMITIDA: {path}")
        return True
    
    def validate_directory(self, path):
        """Valida si se puede crear un directorio"""
        # Verificar que el padre está permitido
        parent = os.path.dirname(path)
        
        allowed, error = self.is_path_allowed(parent or path)
        if not allowed:
            raise SecurityError(f"DIRECTORIO DENEGADO: {error}")
        
        logger.info(f"DIRECTORIO PERMITIDO: {path}")
        return True


class FetchValidator:
    """Validador para el Fetch MCP"""
    
    def __init__(self, config_path='/home/user/.openclaw/workspace/config/security.json'):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.allowed_domains = self.config['fetch']['allowed_domains']
        self.blocked_domains = self.config['fetch']['blocked_domains']
        self.max_chars = self.config['fetch']['max_chars']
    
    def extract_domain(self, url):
        """Extrae el dominio de una URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    
    def validate_url(self, url):
        """Valida si una URL es segura"""
        domain = self.extract_domain(url)
        
        # 1. Verificar dominios bloqueados
        for blocked in self.blocked_domains:
            if fnmatch.fnmatch(domain, blocked):
                raise SecurityError(f"URL BLOQUEADA: Dominio {domain} está bloqueado")
        
        # 2. Verificar que está en dominios permitidos
        allowed = False
        for allowed_pattern in self.allowed_domains:
            if fnmatch.fnmatch(domain, allowed_pattern):
                allowed = True
                break
        
        if not allowed:
            raise SecurityError(f"URL NO PERMITIDA: Dominio {domain} no está en lista blanca")
        
        logger.info(f"URL PERMITIDA: {url}")
        return True


class GitValidator:
    """Validador para el Git MCP"""
    
    def __init__(self, config_path='/home/user/.openclaw/workspace/config/security.json'):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.allowed_commands = self.config['git']['allowed_commands']
        self.blocked_commands = self.config['git']['blocked_commands']
        self.require_confirmation = self.config['git']['require_confirmation']
    
    def validate_command(self, command):
        """Valida si un comando git es seguro"""
        # Normalizar comando - quitar "git " del inicio si existe
        command = command.strip().lower()
        if command.startswith('git '):
            command = command[4:]
        
        # Verificar si el comando contiene comandos bloqueados
        for blocked in self.blocked_commands:
            if blocked.lower() in command:
                raise SecurityError(f"COMANDO GIT BLOQUEADO: {command} está prohibido")
        
        # Verificar que contiene AL MENOS un comando permitido
        allowed = False
        parts = command.split()
        if parts and parts[0] in self.allowed_commands:
            allowed = True
        
        if not allowed:
            raise SecurityError(f"COMANDO GIT NO PERMITIDO: {command}")
        
        # 3. Verificar si requiere confirmación
        for confirm_cmd in self.require_confirmation:
            if confirm_cmd.lower() in command:
                logger.warning(f"COMANDO REQUIERE CONFIRMACIÓN: {command}")
                return "CONFIRM_REQUIRED"
        
        logger.info(f"COMANDO GIT PERMITIDO: {command}")
        return "ALLOWED"


class SQLiteValidator:
    """Validador para el SQLite MCP"""
    
    def __init__(self, config_path='/home/user/.openclaw/workspace/config/security.json'):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.allowed_databases = self.config['sqlite']['allowed_databases']
        self.blocked_operations = self.config['sqlite']['blocked_operations']
    
    def validate_database(self, db_path):
        """Valida si la base de datos está permitida"""
        if db_path not in self.allowed_databases:
            raise SecurityError(f"BASE DE DATOS NO PERMITIDA: {db_path}")
        
        logger.info(f"BASE DE DATOS PERMITIDA: {db_path}")
        return True
    
    def validate_operation(self, sql):
        """Valida una operación SQL"""
        sql_upper = sql.upper()
        
        for blocked in self.blocked_operations:
            if blocked in sql_upper:
                raise SecurityError(f"OPERACIÓN SQL BLOQUEADA: {blocked}")
        
        logger.info(f"OPERACIÓN SQL PERMITIDA: {sql[:50]}...")
        return True


# Instancias globales
path_validator = PathValidator()
fetch_validator = FetchValidator()
git_validator = GitValidator()
sqlite_validator = SQLiteValidator()


def validate_operation(mcp_name, operation, params):
    """
    Valida una operación de MCP.
    
    Args:
        mcp_name: Nombre del MCP (filesystem, fetch, git, sqlite)
        operation: Nombre de la operación
        params: Diccionario con parámetros
    
    Returns:
        dict con resultado de validación
    """
    result = {
        "allowed": False,
        "message": "",
        "warning": False
    }
    
    try:
        if mcp_name == "filesystem":
            operation_type = operation.replace("filesystem.", "")
            
            if operation_type in ["read_text_file", "read_file", "read_media_file", "read_multiple_files"]:
                path_validator.validate_read(params.get("path", ""))
            
            elif operation_type in ["write_file", "edit_file"]:
                path_validator.validate_write(params.get("path", ""))
            
            elif operation_type == "create_directory":
                path_validator.validate_directory(params.get("path", ""))
            
            elif operation_type == "move_file":
                path_validator.validate_read(params.get("source", ""))
                path_validator.validate_write(params.get("destination", ""))
            
            result["allowed"] = True
        
        elif mcp_name == "fetch":
            if operation == "fetch.fetch":
                fetch_validator.validate_url(params.get("url", ""))
            
            result["allowed"] = True
        
        elif mcp_name == "git":
            # Para git, validamos el comando
            result["allowed"] = True  # El comando ya fue validado antes de llamar
        
        elif mcp_name == "sqlite":
            if operation == "sqlite.execute_sql":
                sqlite_validator.validate_operation(params.get("sql", ""))
            
            result["allowed"] = True
        
        else:
            result["message"] = f"MCP desconocido: {mcp_name}"
    
    except SecurityError as e:
        result["allowed"] = False
        result["message"] = str(e)
    
    return result


if __name__ == "__main__":
    # Testing
    print("=== Testing Security Validator ===\n")
    
    # Test 1: Path permitido
    print("Test 1: Path permitido")
    try:
        path_validator.validate_read("/home/user/.openclaw/workspace/data/test.csv")
        print("✅ PASSED\n")
    except SecurityError as e:
        print(f"❌ FAILED: {e}\n")
    
    # Test 2: Path bloqueado
    print("Test 2: Path bloqueado (~/.ssh)")
    try:
        path_validator.validate_read("~/.ssh/id_rsa")
        print("❌ FAILED: Debería haber sido bloqueado\n")
    except SecurityError as e:
        print(f"✅ PASSED: {e}\n")
    
    # Test 3: URL permitida
    print("Test 3: URL permitida (GitHub)")
    try:
        fetch_validator.validate_url("https://github.com/anthropic/claude-code")
        print("✅ PASSED\n")
    except SecurityError as e:
        print(f"❌ FAILED: {e}\n")
    
    # Test 4: URL bloqueada
    print("Test 4: URL bloqueada (localhost)")
    try:
        fetch_validator.validate_url("http://localhost:8080/secret")
        print("❌ FAILED: Debería haber sido bloqueado\n")
    except SecurityError as e:
        print(f"✅ PASSED: {e}\n")
    
    # Test 5: Comando git permitido
    print("Test 5: Comando git permitido (git status)")
    try:
        result = git_validator.validate_command("git status")
        print(f"✅ PASSED: {result}\n")
    except SecurityError as e:
        print(f"❌ FAILED: {e}\n")
    
    # Test 6: Comando git bloqueado
    print("Test 6: Comando git bloqueado (git push)")
    try:
        git_validator.validate_command("git push origin main")
        print("❌ FAILED: Debería haber sido bloqueado\n")
    except SecurityError as e:
        print(f"✅ PASSED: {e}\n")
    
    print("=== Tests Completados ===")
