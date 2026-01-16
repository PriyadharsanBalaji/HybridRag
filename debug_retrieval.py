"""
Debug script to check what's in ChromaDB
"""
from database.chroma_manager import chroma_manager
from src.embeddings import embedding_manager

# Check collection
stats = chroma_manager.get_stats()
print(f"📊 Total documents in ChromaDB: {stats['total_documents']}")

# Try to peek at some documents
try:
    results = chroma_manager.collection.peek(limit=5)
    print(f"\n📄 Sample documents:")
    for i, doc in enumerate(results.get('documents', [])[:3]):
        print(f"\nDocument {i+1}:")
        print(f"Content preview: {doc[:200]}...")
        print(f"Metadata: {results.get('metadatas', [[]])[i]}")
except Exception as e:
    print(f"❌ Error peeking: {e}")

# Test a query
test_query = "what is this document about"
print(f"\n🔍 Testing query: '{test_query}'")

try:
    query_embedding = embedding_manager.embed_text(test_query)
    print(f"✅ Query embedding generated: dimension {len(query_embedding)}")
    
    results = chroma_manager.collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\n📊 Query returned {len(results['documents'][0])} results")
    
    if results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            distance = results['distances'][0][i]
            similarity = 1 - distance
            print(f"\nResult {i+1}:")
            print(f"Similarity: {similarity:.3f}")
            print(f"Distance: {distance:.3f}")
            print(f"Content: {doc[:150]}...")
    else:
        print("❌ No results returned!")
        
except Exception as e:
    print(f"❌ Query error: {e}")
    import traceback
    traceback.print_exc()
