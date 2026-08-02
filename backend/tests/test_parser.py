import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.parser.ast_parser import command_parser

def test_ast_parser_standard_rm():
    cmd = "sudo rm -rf /var/log/*"
    meta = command_parser.parse(cmd)
    assert meta.base_command == "rm"
    assert meta.is_sudo is True
    assert meta.is_recursive is True
    assert meta.is_force is True
    assert meta.target_is_wildcard is True
    assert "/var/log/*" in meta.targets

def test_ast_parser_chmod_777():
    cmd = "chmod -R 777 /etc"
    meta = command_parser.parse(cmd)
    assert meta.base_command == "chmod"
    assert meta.is_recursive is True
    assert meta.is_sudo is False
    assert "/etc" in meta.targets

def test_ast_parser_obfuscation_base64():
    cmd = "echo c3VkbyBybSAtcmYgLw== | base64 -d | bash"
    meta = command_parser.parse(cmd)
    assert meta.is_obfuscated is True
    assert meta.clean_command == "sudo rm -rf /"
    assert meta.base_command == "rm"
    assert meta.is_recursive is True

def test_ast_parser_obfuscation_quotes():
    cmd = "r''m -r\"\"f /"
    meta = command_parser.parse(cmd)
    assert meta.is_obfuscated is True
    assert meta.clean_command == "rm -rf /"
    assert meta.base_command == "rm"

@pytest.mark.anyio
async def test_parse_api_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/parser/parse", json={"command": "sudo rm -rf /home"})
    assert response.status_code == 200
    data = response.json()
    assert data["base_command"] == "rm"
    assert data["is_sudo"] is True
    assert data["is_recursive"] is True
