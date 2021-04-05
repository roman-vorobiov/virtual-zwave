class Backend {
    constructor(url) {
        this.ws = new WebSocket(url);
        this.subscribers = {};

        this.ws.onopen = () => {
            this.sendData({
                messageType: "GET_NODES",
                message: {}
            });
        };

        this.ws.onmessage = (event) => {
            let data = JSON.parse(event.data);
            console.log(data);

            let messageType = data.messageType;
            let message = data.message;

            this.subscribers[messageType]?.forEach(subscriber => {
                subscriber(message);
            });
        };
    }

    sendData(data) {
        console.log(data);
        this.ws.send(JSON.stringify(data));
    }

    subscribe(messageType, subscriber) {
        let subscribers = this.subscribers[messageType] || (this.subscribers[messageType] = []);
        subscribers.push(subscriber);
    }
};

export default Backend;
