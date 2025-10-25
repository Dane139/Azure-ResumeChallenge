using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Azure.Functions.Worker;
using System.Net;
using System.Text.Json;
using Microsoft.Azure.Functions.Worker.Extensions.CosmosDB;
using Microsoft.Extensions.Logging;

namespace Company.Function 
{
    public static class GetVisitCounter
    {
        [Function("GetVisitCounter")]
        public static HttpResponseData Run(
            [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "counter")] HttpRequestData req,
            
            // 1. INPUT BINDING: Reads the document with Id="1" and maps it to the Counter class
            [CosmosDBInput(
                "AzureResume",        // Database Name (from Chunk 2.3)
                "Counter",            // Container Name (from Chunk 2.3)
                Id = "1",             // Document ID
                PartitionKey = "1",   // Partition Key
                Connection = "AzureResumeConnectionString")] // App Setting Name (from Chunk 4.4)
                Counter counterIn,
            
            // 2. OUTPUT BINDING: Writes the value of counterOut back to Cosmos DB
            [CosmosDBOutput(
                "AzureResume", 
                "Counter", 
                Connection = "AzureResumeConnectionString")]
                out Counter counterOut,
            
            FunctionContext context)
        {
            var logger = context.GetLogger("GetVisitCounter");
            
            if (counterIn == null)
            {
                logger.LogError("Counter item not found in Cosmos DB. Check Chunk 2.4 data seeding.");
                counterOut = null; 
                var errorResponse = req.CreateResponse(HttpStatusCode.InternalServerError);
                errorResponse.WriteString("Error: Counter not found.");
                return errorResponse;
            }

            // 3. LOGIC: Prepare the output object (counterOut) by using the input value and incrementing the count
            // The output binding will automatically save this object once the function returns.
            counterOut = counterIn;
            counterOut.count += 1; 

            // 4. RESPONSE: Return the *old* count (before increment) to the client as JSON
            var response = req.CreateResponse(HttpStatusCode.OK);
            response.Headers.Add("Content-Type", "application/json");
            
            // We return the old value (counterIn) so the visitor sees the count *before* their visit was registered.
            response.WriteString(System.Text.Json.JsonSerializer.Serialize(counterIn)); 
            return response;
        }
    }
}