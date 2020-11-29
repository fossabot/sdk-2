"""Sample tap test for tap-snowflake."""

from pathlib import Path
from tap_base.TapConnectionBase import TapConnectionBase
from typing import Any, Dict, List, Tuple

from tap_base import TapBase
from sample_tap_snowflake.SampleTapSnowflakeStream import SampleTapSnowflakeStream
from sample_tap_snowflake import utils
import snowflake.connector


class SampleTapSnowflakeConnection(TapConnectionBase):
    """Snowflake Tap Connection Class."""

    def query(self, query, params=None, max_records=0):
        """Run a query in snowflake."""
        result = []
        with self.connect_with_backoff() as connection:
            with connection.cursor(snowflake.connector.DictCursor) as cur:
                queries = []
                if isinstance(query, list):
                    # Run every query in one transaction if query is a list of SQL
                    queries.append("START TRANSACTION")
                    queries.extend(query)
                else:
                    queries = [query]
                for sql in queries:
                    # LOGGER.debug("SNOWFLAKE - Running query: %s", sql) # TODO: Add logger
                    cur.execute(sql, params)
                    if max_records and cur.rowcount > max_records:
                        # Raise exception if num rows greater than max allowed records
                        raise TooManyRecordsException(
                            "Query returned too many records. "
                            f"This query can return max {max_records} records."
                        )
                    if cur.rowcount > 0:
                        result = cur.fetchall()
        return result