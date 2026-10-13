// Runs in QtWebEngine's isolated application world, never as a browser command.
(function (request) {
    "use strict";
    try {
        const key = "__qutebrowserRbwOperations";
        const operations = globalThis[key] || (globalThis[key] = new Map());
        if (request.action === "discard") {
            operations.delete(request.handle);
            return "cancelled";
        }
        const visible = input => input instanceof HTMLInputElement && input.isConnected &&
            !input.disabled && !input.readOnly && input.getClientRects().length > 0 &&
            getComputedStyle(input).visibility !== "hidden" && getComputedStyle(input).display !== "none" &&
            (!input.checkVisibility || input.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}));
        if (request.action === "prepare") {
            if (location.href !== request.url || document.activeElement instanceof HTMLIFrameElement)
                return "destination";
            const active = document.activeElement;
            if (!visible(active)) return "form";
            const scope = active.form || document;
            const inputs = Array.from(scope.querySelectorAll("input")).filter(visible);
            const fields = {};
            if (request.mode === "login") {
                const passwords = inputs.filter(input => input.type === "password");
                if (passwords.length !== 1) return "form";
                const names = inputs.filter(input => ["text", "email", "tel"].includes(input.type));
                let users = names.filter(input => input.autocomplete.split(" ").includes("username"));
                if (!users.length) users = names.filter(input => input.type === "email");
                if (!users.length) users = names.filter(input => /^(user(name)?|e-?mail|login)$/i.test(input.name || input.id));
                if (!users.length && names.length === 1) users = names;
                if (users.length !== 1 || (active !== users[0] && active !== passwords[0])) return "form";
                fields.username = users[0]; fields.password = passwords[0];
            } else if (request.mode === "password") {
                if (active.type !== "password") return "form";
                fields.password = active;
            } else if (request.mode === "username" || request.mode === "totp") {
                if (!["text", "email", "tel", "number"].includes(active.type)) return "form";
                fields[request.mode] = active;
            } else return "form";
            const types = Object.fromEntries(Object.entries(fields).map(([name, input]) => [name, input.type]));
            operations.set(request.handle, {url: request.url, document, fields, types});
            return "ready";
        }
        const operation = operations.get(request.handle);
        operations.delete(request.handle);
        if (!operation || operation.document !== document || location.href !== operation.url ||
            document.visibilityState !== "visible" || !document.hasFocus() || Date.now() > request.expiresAt)
            return "destination";
        const pairs = Object.entries(operation.fields);
        if (!pairs.every(([name, input]) => visible(input) && input.type === operation.types[name] && input.ownerDocument === document &&
            typeof request.values[name] === "string")) return "form";
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
        for (const [name, input] of pairs) {
            const probe = document.createElement("input");
            probe.type = input.type;
            setter.call(probe, request.values[name]);
            if (probe.value !== request.values[name]) return "form";
        }
        for (const [name, input] of pairs) {
            // Input handlers may synchronously navigate or replace other fields.
            if (location.href !== operation.url || document.visibilityState !== "visible" || !document.hasFocus() ||
                Date.now() > request.expiresAt || !visible(input) || input.type !== operation.types[name]) return "destination";
            setter.call(input, request.values[name]);
            input.dispatchEvent(new Event("input", {bubbles: true}));
            input.dispatchEvent(new Event("change", {bubbles: true}));
        }
        pairs[pairs.length - 1][1].focus();
        return "filled";
    } catch (_) {
        return "form";
    }
})
