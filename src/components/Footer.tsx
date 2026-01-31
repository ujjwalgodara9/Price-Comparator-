import { Instagram, Linkedin, Facebook, Youtube, Mail } from 'lucide-react';

function XIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden="true">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

const SOCIAL_LINKS = [
  { href: 'https://www.instagram.com/groease/', icon: Instagram, label: 'Instagram' },
  { href: 'https://www.linkedin.com/company/109512140/admin/dashboard/', icon: Linkedin, label: 'LinkedIn' },
  { href: 'https://www.facebook.com/profile.php?id=61583175544357', icon: Facebook, label: 'Facebook' },
  { href: 'https://x.com/groeaseindia', icon: XIcon, label: 'X (Twitter)' },
  { href: 'https://www.youtube.com/channel/UCdxRL9f_mCMxkX6_KUMULNw', icon: Youtube, label: 'YouTube' },
];

export function Footer() {
  return (
    <footer className="mt-auto border-t border-blue-100 bg-gradient-to-r from-white via-blue-50/40 to-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-8">
          {/* Brand & contact */}
          <div className="space-y-3">
            <h3 className="text-xl font-bold text-blue-900">Groease</h3>
            <p className="text-blue-700 text-sm max-w-xs">
              India&apos;s grocery comparison platform.
            </p>
            <a
              href="mailto:Groeaseindia@gmail.com"
              className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              <Mail className="h-4 w-4" />
              Groeaseindia@gmail.com
            </a>
          </div>

          {/* Links */}
          <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
            <a href="#" className="text-blue-600 hover:text-blue-700 hover:underline">
              Privacy Policy
            </a>
            <a href="#" className="text-blue-600 hover:text-blue-700 hover:underline">
              Terms & Conditions
            </a>
            <a href="#" className="text-blue-600 hover:text-blue-700 hover:underline">
              Partner with Us
            </a>
          </div>
        </div>

        {/* Social icons */}
        <div className="mt-8 pt-6 border-t border-blue-100">
          <p className="text-sm text-blue-700 font-medium mb-3">Follow us</p>
          <div className="flex items-center gap-3">
            {SOCIAL_LINKS.map(({ href, icon: Icon, label }) => (
              <a
                key={label}
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2.5 rounded-full bg-blue-50/80 border border-blue-100 text-blue-600 hover:bg-blue-100 hover:text-blue-700 hover:border-blue-200 transition-colors"
                aria-label={label}
              >
                <Icon className="w-5 h-5" />
              </a>
            ))}
          </div>
        </div>

        <p className="mt-6 text-xs text-blue-600/80">© Groease</p>
      </div>
    </footer>
  );
}
