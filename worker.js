/**
 * File:    worker.js
 * Purpose: Cloudflare Worker entry point. Acts as a reverse proxy that
 *          forwards all traffic from the workers.dev URL to the Hugging Face
 *          Spaces deployment. Keeps a permanent, fast Cloudflare URL as the
 *          public-facing endpoint regardless of where the app is hosted.
 * Author:  [Your Name]
 * Date:    [Date]
 *
 * How it works:
 *   1. Browser hits https://ai-support-chatbot.[account].workers.dev
 *   2. This Worker intercepts the request
 *   3. Worker forwards it to the HF Spaces URL defined in HF_SPACE_URL
 *   4. Response is passed back to the browser transparently
 *
 * To update the backend URL: change HF_SPACE_URL below and redeploy.
 * No other files need to change.
 */

// ---------------------------------------------------------------------------
// Configuration — update HF_SPACE_URL when you deploy to Hugging Face Spaces
// Format: https://[hf-username]-[space-name].hf.space
// ---------------------------------------------------------------------------
const HF_SPACE_URL = "https://mrmustseeus-ai-support-chatbot.hf.space";

export default {
  /**
   * Handles every incoming HTTP request.
   * Strips the workers.dev origin and rewrites the URL to point at HF Spaces,
   * then forwards headers and body unchanged.
   *
   * @param {Request} request - The incoming request from the browser
   * @param {object}  env     - Cloudflare environment bindings (vars + secrets)
   * @param {object}  ctx     - Execution context (used for waitUntil tasks)
   * @returns {Promise<Response>}
   */
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Replace the workers.dev origin with the HF Spaces origin.
    // Path, query string, and everything else stays identical.
    const targetUrl = `${HF_SPACE_URL}${url.pathname}${url.search}`;

    // Clone the request with the new URL, preserving method, headers, and body
    const proxiedRequest = new Request(targetUrl, {
      method:  request.method,
      headers: request.headers,
      body:    request.method !== "GET" && request.method !== "HEAD"
                 ? request.body
                 : undefined,
    });

    try {
      const response = await fetch(proxiedRequest);

      // Pass the response back to the browser as-is.
      // Headers (including Content-Type) flow through unchanged.
      return new Response(response.body, {
        status:     response.status,
        statusText: response.statusText,
        headers:    response.headers,
      });

    } catch (error) {
      // Surface fetch errors as a 502 so they're distinguishable from app errors
      console.error("Proxy fetch failed:", error.message);
      return new Response(
        JSON.stringify({ error: "Service temporarily unavailable. Please try again." }),
        {
          status: 502,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
  },
};
