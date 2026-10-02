import pymongo
from pymongo.errors import ConnectionFailure

def main():
    # Try localhost first (if running outside docker but port exposed)
    uri = "mongodb://localhost:27018/phishing_detection_db"
    
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
        # Force a connection check
        client.admin.command('ping')
        db = client["phishing_detection_db"]
        
        print("Connected to MongoDB at", uri)
        print("Database: phishing_detection_db\n")
        
        collections = db.list_collection_names()
        print(f"Total Collections: {len(collections)}")
        print("-" * 40)
        
        for coll_name in sorted(collections):
            count = db[coll_name].count_documents({})
            print(f"Collection: {coll_name:<20} | Documents: {count}")
            
    except ConnectionFailure:
        print("Failed to connect to MongoDB on localhost:27017. Is the Docker container running?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
