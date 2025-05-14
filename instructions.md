# Instructions

I have an api at [this url](https://gwm6c6ucq5.execute-api.eu-west-1.amazonaws.com/prod/query) which given a query like

```json
{
    "query": "Find eocis imagery for Berlin from October 2024"
}
```

Will return a response which starts like the below:

```json
{
    "metadata": {
        "collections": [
            "eocis-lst-s3a-day",
            "eocis-lst-s3a-night",
            "eocis-lst-s3b-day",
            "eocis-lst-s3b-night"
        ],
        "bbox": [
            13,
            52.3,
            13.8,
            52.7
        ],
        "time_period": "2024-10-01T00:00:00Z/2024-10-31T23:59:59Z",
        "total_results": 124
    },
    "results": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "stac_version": "1.0.0",
                "stac_extensions": [
                    "https://stac-extensions.github.io/datacube/v2.2.0/schema.json",
                    "https://stac-extensions.github.io/scientific/v1.0.0/schema.json"
                ],
                "id": "c489e3c5-3685-4bcc-92bf-5ed5554a9ea5",
                "collection": "eocis-lst-s3a-day",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [

                    ```


I would like to generate a front-end using python, that
- has a sidebar on the left and a map display
- Allows a user to type a query in a sidebar on the right
- The api should then be called with the query
- The app should wait for a response (can take up to 30 seconds)
- When the response is recieved
    - the metadata is displayed underneath the query in the sidebar
    - a list of result id's is displayed somewhere
    - when a result id is clicked on a thumbnail of the stac item is displayed on the map and the map zoomed into the result
    - when another result is clicked on the last result dissapears and the map zooms to the next thumbnail
