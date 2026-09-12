const ROUTE_PREFIX = "/inner-mongolia/map";
const UPSTREAM = "https://marinabaysands-agent.github.io/inner-mongolia-map-2026/";

const SECURITY_HEADERS = {
  "Content-Security-Policy": [
    "default-src 'self'",
    "img-src 'self' data: https://webrd01.is.autonavi.com https://webrd02.is.autonavi.com https://webrd03.is.autonavi.com https://webrd04.is.autonavi.com",
    "style-src 'self' 'unsafe-inline'",
    "script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com",
    "connect-src 'self' https://cloudflareinsights.com",
    "font-src 'self'",
    "frame-src 'none'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'none'",
    "frame-ancestors 'none'",
  ].join("; "),
  "Permissions-Policy": "geolocation=(), camera=(), microphone=(), payment=()",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "X-Travel-Map-Edge": "inner-mongolia-v1",
};

function redirectToSlash(url) {
  const target = new URL(url);
  target.pathname = `${ROUTE_PREFIX}/`;
  return Response.redirect(target, 308);
}

function upstreamUrl(requestUrl) {
  const incoming = new URL(requestUrl);
  const relativePath = incoming.pathname.slice(`${ROUTE_PREFIX}/`.length) || "index.html";
  const target = new URL(UPSTREAM);
  // Assign as a pathname, rather than resolving a URL, so a crafted path cannot change the upstream host.
  target.pathname = `${target.pathname}${relativePath}`;
  target.search = incoming.search;
  return target;
}

function upstreamRequest(request, target) {
  const headers = new Headers();
  for (const name of ["Accept", "Accept-Encoding", "If-Modified-Since", "If-None-Match", "Range"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  return new Request(target, {
    method: request.method,
    headers,
    redirect: "follow",
  });
}

function cacheTtl(pathname) {
  if (pathname.endsWith(".html") || pathname.endsWith(".json") || pathname.endsWith("/")) return 300;
  return 86400;
}

function securedResponse(upstream, pathname) {
  const headers = new Headers(upstream.headers);
  headers.delete("Set-Cookie");
  headers.delete("Content-Security-Policy-Report-Only");
  for (const [name, value] of Object.entries(SECURITY_HEADERS)) headers.set(name, value);
  headers.set("Cache-Control", `public, max-age=0, s-maxage=${cacheTtl(pathname)}, must-revalidate, no-transform`);
  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers,
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === ROUTE_PREFIX) return redirectToSlash(url);
    if (!url.pathname.startsWith(`${ROUTE_PREFIX}/`)) return new Response("Not found", { status: 404 });
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", {
        status: 405,
        headers: { Allow: "GET, HEAD" },
      });
    }

    const target = upstreamUrl(url);
    const response = await fetch(upstreamRequest(request, target), {
      cf: {
        cacheEverything: true,
        cacheTtl: cacheTtl(target.pathname),
      },
    });
    return securedResponse(response, target.pathname);
  },
};
