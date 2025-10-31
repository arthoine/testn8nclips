#!/usr/bin/env python3
"""
Script de diagnostic pour tester le serveur LLaVA Video
"""
import requests
import json
import sys

def test_server_health():
    """Test si le serveur répond"""
    print("🔍 Test 1: Vérification de la connexion au serveur...")
    print("-" * 50)
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur LLaVA est UP et répond !")
            print(f"   Réponse: {response.json()}")
            return True
        else:
            print(f"⚠️  Serveur répond mais status bizarre: {response.status_code}")
            return False
    except requests.exceptions.ConnectionRefusedError:
        print("❌ ERREUR: Connexion refusée - Le serveur ne tourne PAS sur le port 5000")
        print("   → Lance le serveur avec: python llava_video_server.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ ERREUR: Timeout - Le serveur ne répond pas assez vite")
        return False
    except Exception as e:
        print(f"❌ ERREUR inattendue: {e}")
        return False

def test_batch_endpoint():
    """Test l'endpoint /batch avec des données factices"""
    print("\n🔍 Test 2: Test de l'endpoint /batch...")
    print("-" * 50)
    
    # Données de test (clips factices)
    test_data = {
        "clips": [
            {
                "video_path": "C:/test/video1.mp4",
                "title": "Test Clip 1",
                "views": 1000,
                "duration": 30,
                "clip_id": "test123"
            }
        ],
        "total": 1
    }
    
    try:
        print(f"📤 Envoi de {len(test_data['clips'])} clip(s) de test...")
        response = requests.post(
            "http://localhost:5000/batch",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint /batch fonctionne !")
            print(f"   Clips analysés: {result.get('total_analyzed', 0)}")
            print(f"   Réponse complète: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"⚠️  Endpoint répond mais erreur: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except requests.exceptions.ConnectionRefusedError:
        print("❌ ERREUR: Connexion refusée sur /batch")
        return False
    except requests.exceptions.Timeout:
        print("❌ ERREUR: Timeout sur /batch (normal si analyse longue)")
        return False
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

def test_port_listening():
    """Vérifie si quelque chose écoute sur le port 5000"""
    print("\n🔍 Test 3: Vérification du port 5000...")
    print("-" * 50)
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    
    if result == 0:
        print("✅ Port 5000 est OUVERT - Un service écoute dessus")
        return True
    else:
        print("❌ Port 5000 est FERMÉ - Aucun service n'écoute")
        print("   → Lance ton serveur LLaVA !")
        return False

def main():
    print("=" * 50)
    print("🎬 DIAGNOSTIC SERVEUR LLAVA VIDEO")
    print("=" * 50)
    print()
    
    # Test 1: Port ouvert ?
    port_ok = test_port_listening()
    
    if not port_ok:
        print("\n" + "=" * 50)
        print("❌ DIAGNOSTIC: Le serveur ne tourne PAS")
        print("=" * 50)
        print("\n📝 SOLUTION:")
        print("   1. Ouvre un terminal")
        print("   2. Va dans le dossier du serveur")
        print("   3. Lance: python llava_video_server.py")
        print("   4. Attends le message 'Server running on port 5000'")
        sys.exit(1)
    
    # Test 2: Endpoint santé
    health_ok = test_server_health()
    
    # Test 3: Endpoint batch
    if health_ok:
        batch_ok = test_batch_endpoint()
    else:
        batch_ok = False
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    print(f"Port 5000:        {'✅ Ouvert' if port_ok else '❌ Fermé'}")
    print(f"Endpoint /health: {'✅ OK' if health_ok else '❌ Échec'}")
    print(f"Endpoint /batch:  {'✅ OK' if batch_ok else '❌ Échec'}")
    
    if port_ok and health_ok and batch_ok:
        print("\n🎉 TOUT FONCTIONNE ! Ton serveur LLaVA est prêt !")
    else:
        print("\n⚠️  Il y a des problèmes - Vérifie les erreurs ci-dessus")

if __name__ == "__main__":
    main()
