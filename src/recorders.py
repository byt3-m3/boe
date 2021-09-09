from collections import Mapping
from typing import Optional, List, Any
from uuid import UUID
from dataclasses import asdict

from eventsourcing.persistence import InfrastructureFactory, ProcessRecorder, ApplicationRecorder, AggregateRecorder, \
    StoredEvent, Notification
from src.utils.pymongo_utils import add_many_items, get_item, get_client, get_database, get_collection


class MongoDatastore:
    def __init__(self,
                 db_host,
                 db_port,
                 db_name,
                 ):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.client = self.get_client()
        self.database = self.get_database()
        self.event_store_collection = self.get_collection(collection_name='event_store')

    def get_client(self):
        return get_client(db_host=self.db_host, db_port=self.db_port)

    def get_database(self):
        return get_database(client=self.client, db_name=self.db_name)

    def get_collection(self, collection_name):
        return get_collection(database=self.database, collection=collection_name)


class MongoAggregateRecorder(AggregateRecorder):

    def __init__(self, datastore: MongoDatastore, events_table_name: str):
        self.datastore = datastore

    def insert_events(self, stored_events: List[StoredEvent], **kwargs: Any) -> None:
        results = add_many_items(
            collection=self.collection,
            items=[asdict(event) for event in stored_events],
            ordered=True,

        )

    def select_events(self, originator_id: UUID, gt: Optional[int] = None, lte: Optional[int] = None,
                      desc: bool = False, limit: Optional[int] = None) -> List[StoredEvent]:
        cursor = get_item(collection=self.collection, item_id=originator_id, item_key='originator_id')

        return self._prepare_return(cursor=cursor)

    @staticmethod
    def _prepare_return(cursor) -> List[StoredEvent]:
        return [
            StoredEvent(
                originator_id=record['originator_id'],
                topic=record['topic'],
                originator_version=record['originator_version'],
                state=record['state']
            ) for record in cursor
        ]

    @staticmethod
    def _build_originator_query(originator_id, originator_version):
        return {
            "originator_id": originator_id,
            "originator_version": originator_version
        }


class MongoApplicationRecorder(MongoAggregateRecorder, ApplicationRecorder):
    def __init__(self, datastore: MongoDatastore, events_table_name: str = "stored_events"):
        pass

    def select_notifications(self, start: int, limit: int) -> List[Notification]:
        pass

    def max_notification_id(self) -> int:
        pass


class MongoProcessRecorder(MongoApplicationRecorder, ProcessRecorder):
    def __init__(self, datastore: MongoDatastore, events_table_name: str, tracking_table_name: str, ):
        pass

    def max_tracking_id(self, application_name: str) -> int:
        pass


class MongoRecorderFactory(InfrastructureFactory):

    def __init__(self, application_name: str, env: Mapping):
        super().__init__(application_name, env)
        self.MONGO_DB_HOST = env.get("MONGO_DB_HOST")
        self.MONGO_DB_PORT = env.get("MONGO_DB_PORT")
        self.MONGO_DB_NAME = env.get("MONGO_DB_NAME")

        self.datastore = MongoDatastore(
            db_host=self.MONGO_DB_HOST,
            db_port=self.MONGO_DB_PORT,
            db_name=self.MONGO_DB_NAME
        )

    def aggregate_recorder(self, purpose: str = "events") -> AggregateRecorder:
        prefix = self.application_name.lower() or "stored"
        events_table_name = prefix + "_" + purpose
        return MongoAggregateRecorder(datastore=self.datastore, events_table_name=events_table_name)

    def application_recorder(self) -> ApplicationRecorder:
        prefix = self.application_name.lower() or "stored"
        events_table_name = prefix + "_events"
        return MongoApplicationRecorder(datastore=self.datastore, events_table_name=events_table_name)

    def process_recorder(self) -> ProcessRecorder:
        prefix = self.application_name.lower() or "stored"
        events_table_name = prefix + "_events"
        prefix = self.application_name.lower() or "notification"
        tracking_table_name = prefix + "_tracking"
        return MongoProcessRecorder(
            datastore=self.datastore,
            events_table_name=events_table_name,
            tracking_table_name=tracking_table_name
        )
