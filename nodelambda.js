const AWS = require('aws-sdk');
const logs = new AWS.CloudWatchLogs();

// Preconfigured log group (secure)
const LOG_GROUP_NAME = process.env.LOG_GROUP_NAME || '/aws/codebuild/github-runner-logs';

exports.handler = async (event, context) => {
  // Handle OPTIONS request for CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
      },
      body: ''
    };
  }

  try {
    const params = event.queryStringParameters || {};

    // Extract user-provided filters
    const runId = params.run_id;
    const repoName = params.repo_name;
    const jobName = params.job_name;
    const fromTime = params.from;
    const toTime = params.to;

    // Convert timestamps to milliseconds
    let startTime = null;
    let endTime = null;

    if (fromTime) {
      startTime = Math.floor(new Date(fromTime.replace('Z', '+00:00')).getTime());
    }
    if (toTime) {
      endTime = Math.floor(new Date(toTime.replace('Z', '+00:00')).getTime());
    }

    // Build stream name filter
    const filters = [runId, repoName, jobName].filter(f => f);

    // Fetch matching log streams
    const matchingStreams = [];
    let nextToken = null;

    do {
      const describeParams = {
        logGroupName: LOG_GROUP_NAME
      };
      
      if (nextToken) {
        describeParams.nextToken = nextToken;
      }

      const describeResponse = await logs.describeLogStreams(describeParams).promise();

      for (const stream of describeResponse.logStreams || []) {
        const name = stream.logStreamName;
        if (filters.every(f => name.includes(f))) {
          matchingStreams.push(name);
        }
      }

      nextToken = describeResponse.nextToken;
    } while (nextToken);

    if (matchingStreams.length === 0) {
      return {
        statusCode: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ logStreams: [] })
      };
    }

    // Fetch log events for each matching stream
    const result = { logStreams: [] };

    for (const streamName of matchingStreams) {
      const getLogsParams = {
        logGroupName: LOG_GROUP_NAME,
        logStreamName: streamName,
        startFromHead: true
      };

      if (startTime) {
        getLogsParams.startTime = startTime;
      }
      if (endTime) {
        getLogsParams.endTime = endTime;
      }

      const response = await logs.getLogEvents(getLogsParams).promise();

      const events = (response.events || []).map(e => ({
        timestamp: new Date(e.timestamp).toISOString(),
        message: e.message
      }));

      result.logStreams.push({
        name: streamName,
        events: events
      });
    }

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(result)
    };

  } catch (error) {
    console.error('Error:', error.message);
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ error: error.message })
    };
  }
};
