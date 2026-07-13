import Link from "next/link";

import { Logo } from "@/components/layout/logo";
import { Separator } from "@/components/ui/separator";
import { APP_NAME, ROUTES } from "@/config";

import { FOOTER, NAV_LINKS } from "../data/content";

/** Landing page footer. */
export function FooterSection() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t bg-muted/10 px-4 py-12 pb-safe sm:px-6">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
          <div>
            <Link href={ROUTES.home}>
              <Logo />
            </Link>
            <p className="mt-3 max-w-xs text-sm text-muted-foreground">{FOOTER.tagline}</p>
          </div>

          <div className="flex flex-wrap gap-12">
            <div>
              <p className="text-sm font-medium">Product</p>
              <ul className="mt-3 space-y-2">
                {NAV_LINKS.map((link) => (
                  <li key={link.href}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
                <li>
                  <Link
                    href={ROUTES.chat}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    Open app
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <p className="text-sm font-medium">Resources</p>
              <ul className="mt-3 space-y-2">
                {FOOTER.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                      target={link.href.startsWith("http") ? "_blank" : undefined}
                      rel={link.href.startsWith("http") ? "noopener noreferrer" : undefined}
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <Separator className="my-8" />

        <p className="text-center text-xs text-muted-foreground">
          © {year} {APP_NAME}. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
