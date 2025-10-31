import requests
import json
import sys

"""
🧪 TESTEUR SIMPLE - Video Clip Analyzer
Vérifie que le serveur d'analyse fonctionne correctement
"""

SERVER_URL = "http://localhost:5000"

def test_health():
    """Test 1: Vérifier que le serveur répond"""
    print("🔍 Test 1: Health Check...")
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        data = response.json()
        
        if data.get("status") == "ok":
            print(f"✅ Serveur OK")
            print(f"   Model loaded: {data.get('model_loaded')}")
            print(f"   Device: {data.get('device')}")
            return True
        else:
            print(f"❌ Serveur ne répond pas correctement")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter au serveur")
        print(f"   Assurez-vous que le serveur tourne sur {SERVER_URL}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_analyze_single():
    """Test 2: Analyser un clip (si vous en avez un)"""
    print("\n🔍 Test 2: Analyse d'un clip...")
    print("⚠️  Pour ce test, il faut un vrai fichier vidéo")
    
    video_path = input("Chemin vers un clip de test (ou Enter pour sauter): ").strip()
    
    if not video_path:
        print("⏭️  Test sauté")
        return True
    
    try:
        payload = {
            "video_path": video_path,
            "title": "Test Clip",
            "views": 1000,
            "duration": 30
        }
        
        print(f"📤 Envoi de la requête...")
        response = requests.post(
            f"{SERVER_URL}/analyze",
            json=payload,
            timeout=120  # 2 minutes max
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analyse réussie!")
            print(f"   Score: {data.get('score', 'N/A')}/100")
            print(f"   Raison: {data.get('reason', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout - L'analyse prend trop de temps")
        print(f"   Le modèle est peut-être en train de charger la première fois")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_batch_empty():
    """Test 3: Test batch avec liste vide"""
    print("\n🔍 Test 3: Batch vide...")
    try:
        payload = {"clips": []}
        response = requests.post(
            f"{SERVER_URL}/batch",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("clips") == []:
                print(f"✅ Batch vide OK")
                return True
        
        print(f"❌ Réponse inattendue")
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    print("=" * 60)
    print("   VIDEO CLIP ANALYZER - TESTS")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    # Test 2: Analyse single (optionnel)
    if results[0][1]:  # Si health check OK
        results.append(("Analyze Single", test_analyze_single()))
    
    # Test 3: Batch vide
    if results[0][1]:
        results.append(("Batch Empty", test_batch_empty()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("   RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("\nVotre serveur est prêt à être utilisé avec n8n.")
        print(f"\nURL du serveur: {SERVER_URL}")
        print("Endpoint pour n8n: POST /batch")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("\nVérifiez:")
        print("1. Le serveur est bien démarré (python analyzer.py)")
        print("2. Le modèle est correctement téléchargé")
        print("3. CUDA est disponible (nvidia-smi)")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
