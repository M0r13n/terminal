/* Config */
const WELCOME_GREETING = "Welcome to WebShell.😀\n" +
    "You need to solve the following questions with a " + apply_color("SINGLE", "red", "gu") + " line of bash.\n\n" +
    "You can clear the terminal by typing " + apply_color('clear', "blue") + ".\n" +
    "You can go to the about page by typing " + apply_color('about', "blue") + ".\n" +
    "If you find a bug you can type " + apply_color('bug', "blue") + " and submit a bug report!\n" +
    "If you need help, you can type " + apply_color('help', "blue") + ".\n\n" +
    apply_color("Good luck!\n", "green", "gbu");

const WELCOME_BACK_GREETING = "Welcome back to WebShell.😀\n" +
    "You can continue right where you left off!\n\n" +
    "Remember: If you need help, you can type " + apply_color("help", "blue", "u") + ".\n";

const terminal_config = {
    TAB_COMPLETION: ["find", "echo", "awk", "sed", "wc", "grep", "cat", "sort", "cut", "ls", "rm", "less", "head", "tail"],
    GREETINGS: WELCOME_GREETING,
    NAME: "Webshell",
}

const server_config = {
    API_URL: "https://api.command-line.online/",
    //API_URL: "http://localhost:5000/",
}

/* Supported Text effects and style options for apply_color function */
const TEXT_UNDERLINE = "u",
    TEXT_STRIKE = "s",
    TEXT_OVERLINE = "o",
    TEXT_ITALIC = "i",
    TEXT_BOLD = "b",
    TEXT_GLOW = "g";


/**
 * Create a colored message with optional effects.
 */
function apply_color(message, color = "", effect = "") {
    return "[[" + effect + ";" + color + ";black]" + message + "]";
}

/**
 * Convert a JSON object with keys into a list.
 * >>> {a: {val:1}, b:{val:4}} --> [{val:1}, {val:4}]
 */
function json_to_list(json_obj) {
    let list = [];
    for (const key in json_obj) {
        list.push(json_obj[key]);
    }
    return list;
}

/**
 * Prepend '#' to each line of a multi-line string
 */
function format_description(text) {
    return "# Question:\n# " + text.match(/[^\r\n]+/g).join("\n# ");
}

function cleanup() {
    localStorage.removeItem('uuid');
    location.reload();
}

/**
 * Pull all challenges from Server as JSON
 */
async function get_challenges() {
    const url = server_config.API_URL + "challenge/list";
    const response = await fetch(url, {
        method: 'GET',
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
    });
    return await response.json();
}

/**
 * Create an image tag
 */
function create_img(id, alt, src, classList, description = '') {
    const img = new Image(0, 0);
    img.id = id;
    img.alt = alt;
    img.src = src
    img.classList = classList;
    img.title = description;
    return img;
}


/* Classes */

class Command {
    constructor(command, challenge) {
        this.command = command;
        this.challenge = challenge;
        this.sanitize();
    }

    get isValid() {
        return (this.command.length > 0);
    }


    sanitize() {
        // replace leading and trailing whitespaces
        this.command = this.command.replace(/^\s+|\s+$/g, '');
    }

    get json() {
        if (this.isValid) {
            return JSON.stringify({command: this.command, challenge: this.challenge});
        }

    }
}

class ChallengeIterator {
    /**
     * Custom iterator-like object that makes it much easier to keep track of all challenges and their current state.
     * The challenge-json is converted into an array on init.
     */
    constructor(challenges) {
        this.challenges_json = challenges;
        this.challenges_list = json_to_list(challenges);
        this.current_index = 0;
        this.length = this.challenges_list.length;
    }

    /**
     * If there are remaining challenges get them.
     */
    next() {
        if (this.has_next_challenge()) {
            return this.challenges_list[++this.current_index];
        }
        return null; // no remaining challenges
    }

    has_next_challenge() {
        return this.current_index < this.length - 1;
    }

    get current_challenge() {
        return this.challenges_list[this.current_index];
    }

    get current_challenge_id() {
        return this.current_challenge.identifier;
    }


}

class Badge {

    static async fetch_badges() {
        const url = server_config.API_URL + "badges/list";
        const response = await fetch(url, {
            method: 'GET',
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
        });
        const response_json = await response.json();
        return Object.keys(response_json).map((key) => {
            return Badge.from_json(response_json[key]);
        });
    }

    static from_json(response_json) {
        return new Badge(response_json.id, response_json.name, response_json.src_filename, response_json.description)
    }

    constructor(id, name, src_filename, description = "") {
        this.id = id;
        this.name = name;
        this.description = description;
        this.src_filename = src_filename;
        this.active_svg = null;
        this.inactive_svg = null;
        this.enabled = false;
        this.init();
        Badge.enable_badges()
    }

    static enable_badges() {
        // remove disabled attr
        document.getElementById(Badge.CONTAINER_ID).classList.toggle("disabled", false);
    }

    static get CONTAINER_ID() {
        return "badgeContainer";
    }

    init() {
        this.add_svgs();
    }

    get active_src() {
        return "svg/" + this.src_filename + "_green.svg";
    }

    get inactive_src() {
        return "svg/" + this.src_filename + "_gray.svg";
    }

    /**
     * Adds two images:
     *      <img src="svg/medal_a_gray.svg" alt="medal badge" id="badge-a-disabled">
     *      <img class="disabled" src="svg/medal_a_green.svg" alt="medal badge" id="badge-a-enabled">
     */
    add_svgs() {
        this.inactive_svg = create_img(this.name + "-disabled", "medal badge", this.inactive_src, [], this.description);
        this.active_svg = create_img(this.name + "-enabled", "medal badge", this.active_src, ["disabled"], this.description);
        const containerElement = document.getElementById("badgeContainer");
        containerElement.append(this.active_svg, this.inactive_svg)
    }

    enable() {
        if (this.enabled) {
            return;
        }
        this.active_svg.classList.toggle("disabled", false);
        this.active_svg.classList.add("unlocked");
        this.inactive_svg.classList.toggle("disabled", true);
        this.enabled = true;
    }

    disable() {
        this.active_svg.classList.toggle("disabled", true);
        this.inactive_svg.classList.toggle("disabled", false);
    }
}

class Progressbar {


    constructor(id = "progressbar") {
        this._percentage = 1;
        this.id = id;
        this.span = null;
        this.create_element();
        this.update();
        this.show();
    }

    create_element() {
        /*<div id="progressbar" class="meter"><span style="width: 0%"></span></div>*/
        this.div.classList.toggle("meter", true);
        this.span = document.createElement("span");
        this.div.appendChild(this.span);
    }

    show() {
        document.getElementById(this.id).classList.toggle("disabled", false);
    }

    get div() {
        return document.getElementById(this.id);
    }

    get percentage() {
        return this._percentage;
    }

    get percentage_string() {
        return `${this._percentage}%`;
    }

    set percentage(p) {
        if ((p < 0) || (p > 100)) {
            throw new Error("Value must be between (0) and (100)");
        }
        this._percentage = p.toFixed(0); // round to non decimal
        this.update();
    }

    update() {
        this.span.style.width = this.percentage_string;
    }
}


class CommandlineEngine {
    /**
     * Terminal engine.
     * This class stores the current state of the application and is also handling the parsing, validating and submitting of user input.
     */
    constructor(challenges) {
        this.terminal = null;
        this.challenges = new ChallengeIterator(challenges);
        this.uuid = null;
        this.mode = null;
        this.badges = null;
        this.progressbar = null;
    }

    /**
     * State is stored on the server side for each user and it's uuid.
     * Things to recover:
     *  - Solved Challenges
     *  - Game-Mode
     *  - Earned badges
     *  - Current Progress (can be computed from solved challenges)
     */
    async restore(uuid) {
        console.log("Found existing user. Restoring session...")
        try {
            const state_url = server_config.API_URL + `user/${uuid}/state`;
            const response = await this.http_get(state_url);
            if (!response.ok)
                return;
            const state = await response.json();
            this.mode = state.mode;
            this.uuid = uuid;
            this.challenges.current_index = Math.max(state.solved_challenges.length, 0);
            await this.load_resources();
            if (this.mode === "BADGE") {
                this.set_badges_active(state.badges);
            }
            console.log("Successfully restored user: " + uuid);
            terminal_config.GREETINGS = WELCOME_BACK_GREETING;
        } catch (e) {
            console.error(e);
            this.uuid = null;
        }
    }

    async http_get(url) {
        return await (fetch(url, {
            method: 'GET',
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
            headers: {
                'X-UUID': this.uuid
            }
        }));
    }

    async http_post(url, data) {
        return await fetch(url, {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            headers: {
                'Content-Type': 'application/json',
                'X-UUID': this.uuid
            },
            referrerPolicy: 'no-referrer',
            body: data
        });
    }

    async init() {
        const uuid = localStorage.getItem('uuid');
        if (uuid) {
            await this.restore(uuid);
        }
        if (!this.uuid) {
            console.log("No existing session found. Creating new one...");
            await this.create_session();
            await this.load_resources();
            // set this id to later remember the user
            localStorage.setItem('uuid', this.uuid);
        }
        this.update();
    }

    async load_resources() {
        if (this.mode === "BADGE") {
            this.badges = await Badge.fetch_badges();
        } else if (this.mode === "PROGRESSBAR") {
            this.progressbar = new Progressbar();
        }
    }

    /**
     * Create a new session and get settings fot this session from server.
     */
    async create_session() {
        const settings = await this.register();
        this.uuid = settings.uuid;
        this.mode = settings.mode;
    }

    /**
     * Ask the server for game data.
     * Expects a response like: {"uuid": 1234, "mode":"BADGE"}
     */
    async register() {
        const url = server_config.API_URL + "session/new";
        const response = await this.http_get(url);
        return await response.json();
    }

    /**
     * Submission handler.
     * Parses the command, sends it to the execution server and handles the response.
     */
    async handle_submit(command) {
        if (this.check_builtins(command)) {
            return;
        }
        const cur_command = new Command(command, this.challenges.current_challenge_id);
        const url = server_config.API_URL + "command/run";
        try {
            const response = await (await this.http_post(url, cur_command.json)).json();
            if (response.error) {
                this.error(response.error);
            } else {
                this.handle_command_result(response);
            }
        } catch (e) {
            this.error(e);
        }
    }

    /**
     * Builtin command handlers
     */
    check_builtins(command) {
        if (command.trim() === 'help') {
            const help_text = this.challenges.current_challenge.help;
            const external_link = this.challenges.current_challenge.external_link;
            if (!help_text && !external_link) {
                this.echo("No help available. You're on your own.");
            }
            if (help_text) {
                this.echo(help_text);
            }
            if (external_link) {
                this.echo("You might take a look at this resource: " + apply_color(external_link, "blue", TEXT_GLOW + TEXT_UNDERLINE + TEXT_ITALIC));
            }
            return true;
        } else if (command.trim() === 'about') {
            window.location.href = "/about.html";
            return true;
        } else if (command.trim() === 'bug') {
            window.location.href = "/report.html";
            return true;
        }
        return false;
    }


    /**
     * The function should be called once the the initialization is completed
     */
    ready() {
        this.display_challenge_description();
    }

    /**
     * Echo some message to the terminal instance (formatted in grey)
     */
    echo(msg) {
        if (this.terminal) {
            this.terminal.echo(apply_color(msg, "gray"));
        }
    }

    /**
     * Echo some error message (formatted in red) to the terminal instance
     */
    error(msg) {
        this.terminal.echo(apply_color(msg, "red"));
    }

    /**
     * Echo some success message (formatted in green with a glow effect) to the terminal instance
     */
    success(msg) {
        this.terminal.echo(apply_color(msg, "green", TEXT_GLOW));
    }

    /**
     * Echo the current challenge description.
     * The description is formatted like a command in the bash scripting language (leading #).
     * Every line is prepended with a leading '#'.
     */
    display_challenge_description() {
        if (this.challenges.current_challenge) {
            const description = format_description(this.challenges.current_challenge.description);
            this.echo(description);
        } else {
            this.handle_win();
        }
    }

    /**
     * Check if the server responded with an error and update the current game state on success.
     */
    handle_command_result(result) {
        // echo the output of the command that was produced in the docker container
        this.echo(result.output.replace(/\n+$/, ""));
        if (result.badges) {
            this.set_badges_active(result.badges);
        }
        if (result.success) {
            // if the command was solved correctly load the the next challenge
            //this.terminal.clear();
            this.load_next_challenge();
            this.update();
        }
    }

    /**
     * Iterate over objects badges and check if they were reached.
     * @param badges
     */
    set_badges_active(badges) {
        if (!this.badges) {
            return;
        }
        this.badges.forEach((badge, index) => {
            if (badges.indexOf(badge.id) > -1) {
                if (!badge.enabled) {
                    badge.enable();
                    this.echo(apply_color(`\n🎉You earned the ${badge.name} badge🎉`, 'green', TEXT_BOLD + TEXT_UNDERLINE));
                }
            }
        });
    }

    /**
     * Update graphics likes progressbar or badges
     */
    update() {
        if (this.progressbar && this.challenges.current_index > 0) {
            this.progressbar.percentage = (100 / this.challenges.length) * (this.challenges.current_index);
        }
    }

    /**
     * Called when all challenges are solved and there are no remaining tasks.
     */
    handle_win() {
        this.success("Congratulations, you solved all problems\nDo you agree to answer a simple question about the user experience?\n" +
            " If so, please head to https://command-line.online/feedback.html");
        this.terminal.freeze(1); // lock the terminal and don't allow any interaction
    }

    /**
     * Load the next challenge. If there are no challenges handle the win.
     */
    load_next_challenge() {
        this.success("\nGood JOB! You solved the question\n\n", "green");
        if (this.challenges.has_next_challenge()) {
            const challenge = this.challenges.next();
            this.display_challenge_description();
        } else {
            this.handle_win();
        }
    }

}

function init_terminal(terminalEngine) {
    function show_challenge_description(command, term) {
        if (command === "clear") {
            // display the current challenge after each clear command
            if (terminalEngine.challenges.current_challenge) {
                term.echo(apply_color(format_description(terminalEngine.challenges.current_challenge.description), "grey"));
            }
        }
    }

    // Setup function for jQuery-Terminal
    terminalEngine.terminal = $('#terminal').terminal(async (command, term) => {
        term.pause();
        // handle entered commands
        if (command.length) {
            await terminalEngine.handle_submit(command, term);
        }
        term.resume();
    }, {
        inputStyle: 'contenteditable',
        exceptionHandler: function (e, label) {
            if (typeof window.flush == 'undefined') {
                window.flush = 0;
            }
            if (flush++ <= 1) {
                $('<pre>' + e.message + "\n" + e.stack + '</pre>').appendTo('body');
            }
        },
        greetings: terminal_config.GREETINGS, // displays a fixed greeting at the top of the terminal
        convertLinks: true,
        name: terminal_config.NAME,
        prompt: (callback_f) => {
            // custom prompt function (>>>)
            callback_f(apply_color(">>> ", "green"));
        },
        completion: terminal_config.TAB_COMPLETION, // add tab completion
        onAfterCommand: show_challenge_description // onClear does not work for some weird reason ¯\_(ツ)_/¯
    });

    terminalEngine.ready(); // finish the init process and display the first challenge
}

/* SETUP */
jQuery(document).ready(
    async function () {
        try {
            const challenges = await get_challenges();
            const terminalEngine = new CommandlineEngine(challenges);
            await terminalEngine.init();
            // only init the terminal if all setup function succeeded
            init_terminal(terminalEngine);
        } catch (e) {
            console.error("Could not create a new terminal game, because " + e);
            $('#error').toggle('hidden', false);
            throw e;
        }
    }
);


